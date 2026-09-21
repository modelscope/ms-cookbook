"""Reading community API and static site; OAuth credentials never leave this process."""
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
import hashlib
import hmac
import json
import logging
import os
import secrets
import shutil
import sqlite3
import threading
import time
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)

ANALYTICS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS analytics_page_daily(day TEXT NOT NULL, page TEXT NOT NULL, pv INTEGER NOT NULL DEFAULT 0 CHECK(pv >= 0), PRIMARY KEY(day, page));
CREATE TABLE IF NOT EXISTS analytics_visitor_daily(day TEXT NOT NULL, page TEXT NOT NULL, visitor_hash TEXT NOT NULL, PRIMARY KEY(day, page, visitor_hash));
CREATE INDEX IF NOT EXISTS analytics_visitors_page_day ON analytics_visitor_daily(page, day);
CREATE TABLE IF NOT EXISTS analytics_visitor_all_time(visitor_hash TEXT PRIMARY KEY, first_day TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analytics_site_hourly(hour TEXT PRIMARY KEY, pv INTEGER NOT NULL DEFAULT 0 CHECK(pv >= 0));
CREATE TABLE IF NOT EXISTS analytics_visitor_hourly(hour TEXT NOT NULL, visitor_hash TEXT NOT NULL, PRIMARY KEY(hour, visitor_hash));
CREATE INDEX IF NOT EXISTS analytics_visitors_hour ON analytics_visitor_hourly(hour);
'''

class Entry(BaseModel):
    kind: str
    text: str = Field(default='', max_length=2000)
    quote: str = Field(default='', max_length=2000)
    block: int = Field(default=0, ge=0, le=100000)
    start: int = Field(default=0, ge=0, le=1000000)
    end: int = Field(default=0, ge=0, le=1000000)

class Wish(BaseModel):
    text: str = Field(max_length=2000)

class AnalyticsView(BaseModel):
    page: str = Field(min_length=1, max_length=64)
    visitor: str = Field(min_length=16, max_length=128, pattern=r'^[A-Za-z0-9_-]+$')


def create_app(data_dir=None, analytics_runtime_dir=None):
    folder = Path(data_dir or os.getenv('DATA_DIR', ROOT / '.data'))
    folder.mkdir(parents=True, exist_ok=True)
    db_path = folder / 'reading.sqlite3'
    persistent_analytics_path = folder / 'analytics.sqlite3'
    previous_analytics_path = folder / 'analytics.previous.sqlite3'
    if analytics_runtime_dir:
        analytics_runtime = Path(analytics_runtime_dir)
    elif data_dir is not None:
        analytics_runtime = folder / '.analytics-runtime'
    else:
        analytics_runtime = Path(os.getenv('ANALYTICS_RUNTIME_DIR', '/tmp/purplebook-analytics'))
    analytics_runtime.mkdir(parents=True, exist_ok=True)
    analytics_path = analytics_runtime / 'analytics.sqlite3'
    last_snapshot_path = analytics_runtime / 'analytics.last-snapshot.sqlite3'
    analytics_snapshot_lock = threading.Lock()
    analytics_repair_lock = threading.Lock()
    analytics_snapshot_state = {'generation': 0, 'persisted': 0, 'last': 0.0}
    @contextmanager
    def db():
        conn = sqlite3.connect(db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        try:
            with conn: yield conn
        finally:
            conn.close()
    with db() as conn:
        conn.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, sub TEXT UNIQUE NOT NULL, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS entries(id TEXT PRIMARY KEY, chapter TEXT NOT NULL, user_id TEXT NOT NULL REFERENCES users(id), kind TEXT NOT NULL, text TEXT NOT NULL, quote TEXT NOT NULL, block INTEGER NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL, created INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS entries_chapter ON entries(chapter, created);
        CREATE INDEX IF NOT EXISTS entries_user_time ON entries(user_id, created);
        CREATE TABLE IF NOT EXISTS wishes(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), text TEXT NOT NULL, created INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS wishes_user_time ON wishes(user_id, created);
        ''')

    @contextmanager
    def analytics_db():
        conn = sqlite3.connect(analytics_path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA busy_timeout=5000')
        try:
            with conn: yield conn
        finally:
            conn.close()

    def analytics_corruption(error):
        message = str(error).lower()
        return any(marker in message for marker in ('malformed', 'file is not a database', 'database disk image'))

    def check_analytics_database(path):
        with sqlite3.connect(path, timeout=5) as conn:
            result = conn.execute('PRAGMA quick_check').fetchone()[0]
        if result != 'ok': raise sqlite3.DatabaseError(result)

    def remove_runtime_database():
        for sidecar in ('', '-wal', '-shm', '-journal'):
            path = Path(str(analytics_path) + sidecar)
            if path.exists(): path.unlink()

    def copy_sqlite_database(source, destination):
        temporary = analytics_runtime / f'.restore-{secrets.token_hex(6)}.sqlite3'
        try:
            uri = f'file:{source.resolve()}?mode=ro'
            with sqlite3.connect(uri, uri=True, timeout=10) as source_db, sqlite3.connect(temporary) as target_db:
                source_db.backup(target_db)
            check_analytics_database(temporary)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary.replace(destination)
        finally:
            if temporary.exists(): temporary.unlink()

    def quarantine_persistent_database(source, error):
        suffix = f'{int(time.time())}-{secrets.token_hex(4)}'
        backup = folder / f'{source.stem}.corrupt-{suffix}.sqlite3'
        for sidecar in ('', '-wal', '-shm', '-journal'):
            path = Path(str(source) + sidecar)
            if path.exists(): path.replace(Path(str(backup) + sidecar))
        LOGGER.error('Quarantined corrupted analytics snapshot at %s: %s', backup, error)

    def restore_analytics_database():
        remove_runtime_database()
        for source in (persistent_analytics_path, previous_analytics_path):
            if not source.exists(): continue
            try:
                copy_sqlite_database(source, analytics_path)
                LOGGER.info('Restored analytics runtime database from %s', source)
                return True
            except sqlite3.DatabaseError as error:
                if not analytics_corruption(error): raise
                quarantine_persistent_database(source, error)
        return False

    def initialize_analytics_database():
        with analytics_db() as conn:
            result = conn.execute('PRAGMA quick_check').fetchone()[0]
            if result != 'ok': raise sqlite3.DatabaseError(result)
            # SQLite runs on the container's local filesystem. Consistent database
            # snapshots are copied to the Studio's object-backed persistent mount.
            conn.execute('PRAGMA journal_mode=WAL').fetchone()
            conn.execute('PRAGMA synchronous=FULL')
            conn.executescript(ANALYTICS_SCHEMA)
            conn.execute('''
                INSERT OR IGNORE INTO analytics_visitor_all_time(visitor_hash,first_day)
                SELECT visitor_hash,MIN(day) FROM analytics_visitor_daily
                WHERE page='__site__' GROUP BY visitor_hash
            ''')

    def quarantine_runtime_database(error):
        suffix = f'{int(time.time())}-{secrets.token_hex(4)}'
        backup = folder / f'analytics.corrupt-{suffix}.sqlite3'
        if analytics_path.exists():
            temporary = folder / f'.analytics-corrupt-{secrets.token_hex(6)}.tmp'
            shutil.copyfile(analytics_path, temporary)
            temporary.replace(backup)
        remove_runtime_database()
        LOGGER.error('Quarantined corrupted analytics runtime database at %s: %s', backup, error)

    def durable_copy(source, destination):
        temporary = folder / f'.{destination.name}-{secrets.token_hex(6)}.tmp'
        try:
            with source.open('rb') as input_file, temporary.open('wb') as output_file:
                shutil.copyfileobj(input_file, output_file, 1024 * 1024)
                output_file.flush()
                os.fsync(output_file.fileno())
            temporary.replace(destination)
        finally:
            if temporary.exists(): temporary.unlink()

    def snapshot_analytics_database(force=False):
        with analytics_snapshot_lock:
            generation = analytics_snapshot_state['generation']
            if generation == analytics_snapshot_state['persisted'] and persistent_analytics_path.exists(): return False
            if not force and time.monotonic() - analytics_snapshot_state['last'] < 15: return False
            snapshot = analytics_runtime / f'.snapshot-{secrets.token_hex(6)}.sqlite3'
            try:
                with sqlite3.connect(analytics_path, timeout=5) as source_db, sqlite3.connect(snapshot) as target_db:
                    source_db.backup(target_db)
                check_analytics_database(snapshot)
                if last_snapshot_path.exists(): durable_copy(last_snapshot_path, previous_analytics_path)
                durable_copy(snapshot, persistent_analytics_path)
                snapshot.replace(last_snapshot_path)
                analytics_snapshot_state['persisted'] = generation
                analytics_snapshot_state['last'] = time.monotonic()
                return True
            finally:
                if snapshot.exists(): snapshot.unlink()

    restored = restore_analytics_database()
    try:
        initialize_analytics_database()
    except sqlite3.DatabaseError as error:
        if not analytics_corruption(error): raise
        quarantine_runtime_database(error)
        restored = restore_analytics_database()
        if not restored: remove_runtime_database()
        initialize_analytics_database()
    analytics_snapshot_state['generation'] = 1
    try:
        snapshot_analytics_database(force=True)
        # Persist the first real view immediately after a container starts.
        analytics_snapshot_state['last'] = 0.0
    except (OSError, sqlite3.DatabaseError):
        LOGGER.exception('Could not persist the initial analytics snapshot')
    key_path = folder / 'session.key'
    if not key_path.exists():
        try:
            with key_path.open('x') as f: f.write(secrets.token_hex(32))
            key_path.chmod(0o600)
        except FileExistsError: pass
    base = os.getenv('APP_BASE_URL') or ('https://' + os.environ['STUDIO_HOST'] if os.getenv('STUDIO_HOST') else 'http://127.0.0.1:7860')
    parsed = urlparse(base)
    if parsed.scheme not in ('https', 'http') or not parsed.netloc or parsed.path not in ('', '/'):
        raise RuntimeError('APP_BASE_URL must be an origin without a path')
    if parsed.scheme != 'https' and parsed.hostname not in ('127.0.0.1', 'localhost'):
        raise RuntimeError('Public OAuth deployments require HTTPS')
    base = base.rstrip('/')

    @asynccontextmanager
    async def lifespan(_app):
        yield
        try:
            snapshot_analytics_database(force=True)
        except (OSError, sqlite3.DatabaseError):
            LOGGER.exception('Could not persist analytics during shutdown')

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    session_secret = os.getenv('SESSION_SECRET') or key_path.read_text()
    app.add_middleware(SessionMiddleware, secret_key=session_secret, session_cookie='purplebook_session', max_age=7*86400, same_site='lax', https_only=parsed.scheme=='https')
    oauth = OAuth()
    enabled = bool(os.getenv('OAUTH_CLIENT_ID') and os.getenv('OAUTH_CLIENT_SECRET'))
    if enabled:
        # Studio can inject an internal issuer alias. Use the verified public
        # ModelScope discovery endpoint so redirects remain browser-accessible.
        provider = 'https://www.modelscope.cn'
        oauth.register(name='modelscope', client_id=os.environ['OAUTH_CLIENT_ID'], client_secret=os.environ['OAUTH_CLIENT_SECRET'], server_metadata_url=provider+'/.well-known/openid-configuration', client_kwargs={'scope':'openid profile'})
    raw = (ROOT / 'assets/content.js').read_text().split('=',1)[1].strip().rstrip(';')
    book_data = json.loads(raw)
    # Keep notes attached to their original article when display numbers change.
    chapters = {c['id']: c.get('discussionId', c['id']) for c in book_data['chapters'] if c.get('status') != 'pending'}
    admins = set(filter(None, os.getenv('MODERATOR_SUBS','').split(',')))
    analytics_pages = {'home','contents','paths','practice','contribute'} | {c['id'] for c in book_data['chapters']}
    analytics_titles = {'home':'首页','contents':'全书目录','paths':'阅读路径','practice':'真实任务库','contribute':'社区共建'}
    analytics_titles.update({c['id']:c['title'] for c in book_data['chapters']})
    analytics_timezone = ZoneInfo('Asia/Shanghai')
    analytics_lock = threading.Lock()
    analytics_cleanup_day = {'value': ''}

    def repair_analytics_database(original_error):
        if not analytics_corruption(original_error): raise original_error
        with analytics_repair_lock:
            try:
                check_analytics_database(analytics_path)
                return
            except sqlite3.DatabaseError as error:
                if not analytics_corruption(error): raise
                current_error = error
            quarantine_runtime_database(current_error)
            restored = restore_analytics_database()
            if not restored: remove_runtime_database()
            initialize_analytics_database()
            with analytics_snapshot_lock:
                analytics_snapshot_state['generation'] += 1
            snapshot_analytics_database(force=True)

    def use_analytics_database(operation):
        try:
            return operation()
        except sqlite3.DatabaseError as error:
            if not analytics_corruption(error):
                raise HTTPException(503, '统计服务暂时不可用，请稍后重试') from error
            try:
                repair_analytics_database(error)
                return operation()
            except sqlite3.DatabaseError as retry_error:
                raise HTTPException(503, '统计服务暂时不可用，请稍后重试') from retry_error

    def mark_analytics_dirty():
        with analytics_snapshot_lock:
            analytics_snapshot_state['generation'] += 1
        try:
            snapshot_analytics_database()
        except (OSError, sqlite3.DatabaseError):
            LOGGER.exception('Could not persist the analytics snapshot; a later view will retry')

    def user(request):
        sid = request.session.get('sid')
        if not sid: return None
        with db() as conn:
            row = conn.execute('SELECT users.* FROM sessions JOIN users ON users.id=sessions.user_id WHERE sessions.id=? AND expires>?', (sid,int(time.time()))).fetchone()
        return dict(row) if row else None
    def public_user(u):
        return {'id':u['id'],'name':u['name'],'moderator':u['sub'] in admins} if u else None
    def require_user(request):
        u=user(request)
        if not u: raise HTTPException(401,'请先使用魔搭账号登录')
        csrf=request.headers.get('x-csrf-token','')
        if request.headers.get('origin') != base or not csrf or not secrets.compare_digest(csrf, request.session.get('csrf','')):
            raise HTTPException(403,'页面已过期，请刷新后重试')
        return u
    def check_chapter(chapter):
        if chapter not in chapters: raise HTTPException(404,'章节不存在或尚未开放')
        return chapters[chapter]
    def require_same_origin(request):
        if request.headers.get('origin') != base:
            raise HTTPException(403,'请求来源无效')
    def analytics_range(days,start,end):
        today=datetime.now(analytics_timezone).date()
        if start or end:
            if not start or not end: raise HTTPException(422,'请选择完整的开始和结束日期')
            try:
                first=datetime.strptime(start,'%Y-%m-%d').date()
                last=datetime.strptime(end,'%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(422,'日期格式无效')
        else:
            last=today;first=today-timedelta(days=days-1)
        span=(last-first).days+1
        if first>last or last>today: raise HTTPException(422,'日期范围无效')
        if span>90: raise HTTPException(422,'一次最多查询 90 天')
        if first<today-timedelta(days=179): raise HTTPException(422,'只能查询最近 180 天的数据')
        return today,first,last,span

    @app.middleware('http')
    async def response_headers(request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
        if request.url.path.startswith(('/api/','/auth/')):
            response.headers['Cache-Control']='no-store'
        return response

    @app.get('/api/session')
    def session(request: Request):
        request.session.setdefault('csrf',secrets.token_urlsafe(32))
        return {'user':public_user(user(request)), 'csrf':request.session['csrf'], 'loginEnabled':enabled}

    @app.post('/api/analytics/view',status_code=204)
    def record_analytics_view(view: AnalyticsView, request: Request):
        require_same_origin(request)
        if view.page not in analytics_pages: raise HTTPException(422,'页面不存在')
        current=datetime.now(analytics_timezone)
        today=current.date()
        day=today.isoformat()
        hour=current.strftime('%Y-%m-%dT%H')
        visitor_hash=hmac.new(session_secret.encode(),view.visitor.encode(),hashlib.sha256).hexdigest()
        def write_view():
            with analytics_db() as conn:
                conn.execute('BEGIN IMMEDIATE')
                conn.execute('INSERT INTO analytics_page_daily(day,page,pv) VALUES (?,?,1) ON CONFLICT(day,page) DO UPDATE SET pv=pv+1',(day,view.page))
                conn.execute('INSERT OR IGNORE INTO analytics_visitor_daily(day,page,visitor_hash) VALUES (?,?,?)',(day,view.page,visitor_hash))
                conn.execute('INSERT OR IGNORE INTO analytics_visitor_daily(day,page,visitor_hash) VALUES (?,?,?)',(day,'__site__',visitor_hash))
                conn.execute('INSERT OR IGNORE INTO analytics_visitor_all_time(visitor_hash,first_day) VALUES (?,?)',(visitor_hash,day))
                conn.execute('INSERT INTO analytics_site_hourly(hour,pv) VALUES (?,1) ON CONFLICT(hour) DO UPDATE SET pv=pv+1',(hour,))
                conn.execute('INSERT OR IGNORE INTO analytics_visitor_hourly(hour,visitor_hash) VALUES (?,?)',(hour,visitor_hash))
                with analytics_lock:
                    cleanup=analytics_cleanup_day['value']!=day
                    if cleanup: analytics_cleanup_day['value']=day
                if cleanup:
                    cutoff=(today-timedelta(days=179)).isoformat()
                    conn.execute('DELETE FROM analytics_visitor_daily WHERE day<?',(cutoff,))
                    hourly_cutoff=f'{(today-timedelta(days=89)).isoformat()}T00'
                    conn.execute('DELETE FROM analytics_site_hourly WHERE hour<?',(hourly_cutoff,))
                    conn.execute('DELETE FROM analytics_visitor_hourly WHERE hour<?',(hourly_cutoff,))
        use_analytics_database(write_view)
        mark_analytics_dirty()
        return Response(status_code=204)

    @app.get('/api/analytics/summary')
    def analytics_summary(days: int = Query(7,ge=1,le=90), start: str = '', end: str = ''):
        today,first,last,span=analytics_range(days,start,end)
        first_text,last_text=first.isoformat(),last.isoformat()
        previous_last=first-timedelta(days=1);previous_first=previous_last-timedelta(days=span-1)
        retention_start=today-timedelta(days=179)
        def totals(conn,range_start,range_end):
            bounds=(range_start.isoformat(),range_end.isoformat())
            pv=conn.execute('SELECT COALESCE(SUM(pv),0) total FROM analytics_page_daily WHERE day BETWEEN ? AND ?',bounds).fetchone()['total']
            uv=conn.execute('SELECT COUNT(DISTINCT visitor_hash) total FROM analytics_visitor_daily WHERE page=? AND day BETWEEN ? AND ?',('__site__',*bounds)).fetchone()['total']
            return {'pv':pv,'uv':uv}
        def read_summary():
            with analytics_db() as conn:
                selected=totals(conn,first,last)
                today_totals=totals(conn,today,today)
                previous=totals(conn,previous_first,previous_last) if previous_first>=retention_start else None
                pv_rows={row['day']:row['total'] for row in conn.execute('SELECT day,SUM(pv) total FROM analytics_page_daily WHERE day BETWEEN ? AND ? GROUP BY day',(first_text,last_text))}
                uv_rows={row['day']:row['total'] for row in conn.execute('SELECT day,COUNT(DISTINCT visitor_hash) total FROM analytics_visitor_daily WHERE page=? AND day BETWEEN ? AND ? GROUP BY day',('__site__',first_text,last_text))}
                page_pv={row['page']:row['total'] for row in conn.execute('SELECT page,SUM(pv) total FROM analytics_page_daily WHERE day BETWEEN ? AND ? GROUP BY page ORDER BY total DESC',(first_text,last_text))}
                page_uv={row['page']:row['total'] for row in conn.execute('SELECT page,COUNT(DISTINCT visitor_hash) total FROM analytics_visitor_daily WHERE page!=? AND day BETWEEN ? AND ? GROUP BY page',('__site__',first_text,last_text))}
                lifetime_pv=conn.execute('SELECT COALESCE(SUM(pv),0) total FROM analytics_page_daily').fetchone()['total']
                lifetime_uv=conn.execute('SELECT COUNT(*) total FROM analytics_visitor_all_time').fetchone()['total']
                lifetime_since=conn.execute('SELECT MIN(day) first_day FROM analytics_page_daily').fetchone()['first_day']
            return selected,today_totals,previous,pv_rows,uv_rows,page_pv,page_uv,{'pv':lifetime_pv,'uv':lifetime_uv,'since':lifetime_since}
        selected,today_totals,previous,pv_rows,uv_rows,page_pv,page_uv,lifetime=use_analytics_database(read_summary)
        daily=[]
        cursor=first
        while cursor<=last:
            value=cursor.isoformat();daily.append({'day':value,'pv':pv_rows.get(value,0),'uv':uv_rows.get(value,0)});cursor+=timedelta(days=1)
        pages=[{'page':page,'title':analytics_titles.get(page,page),'pv':pv,'uv':page_uv.get(page,0),'share':round(pv*100/selected['pv'],1) if selected['pv'] else 0} for page,pv in page_pv.items()]
        return {'range':{'start':first_text,'end':last_text,'days':span,'timezone':'Asia/Shanghai'},'lifetime':lifetime,'today':today_totals,'totals':selected,'previous':previous,'daily':daily,'pages':pages,'updatedAt':datetime.now(analytics_timezone).isoformat(timespec='seconds')}

    @app.get('/api/analytics/hourly')
    def analytics_hourly(date: str = ''):
        current=datetime.now(analytics_timezone)
        today=current.date()
        try:
            selected=datetime.strptime(date,'%Y-%m-%d').date() if date else today
        except ValueError as error:
            raise HTTPException(422,'日期格式应为 YYYY-MM-DD') from error
        earliest=today-timedelta(days=89)
        if selected>today: raise HTTPException(422,'不能查询未来日期')
        if selected<earliest: raise HTTPException(422,'小时数据仅保留最近 90 天')
        day=selected.isoformat()
        first_hour=f'{day}T00';last_hour=f'{day}T23'
        def read_hourly():
            with analytics_db() as conn:
                pv_rows={row['hour']:row['pv'] for row in conn.execute('SELECT hour,pv FROM analytics_site_hourly WHERE hour BETWEEN ? AND ?',(first_hour,last_hour))}
                uv_rows={row['hour']:row['total'] for row in conn.execute('SELECT hour,COUNT(*) total FROM analytics_visitor_hourly WHERE hour BETWEEN ? AND ? GROUP BY hour',(first_hour,last_hour))}
                total_pv=conn.execute('SELECT COALESCE(SUM(pv),0) total FROM analytics_site_hourly WHERE hour BETWEEN ? AND ?',(first_hour,last_hour)).fetchone()['total']
                total_uv=conn.execute('SELECT COUNT(DISTINCT visitor_hash) total FROM analytics_visitor_hourly WHERE hour BETWEEN ? AND ?',(first_hour,last_hour)).fetchone()['total']
                available_since=conn.execute('SELECT MIN(hour) first_hour FROM analytics_site_hourly').fetchone()['first_hour']
            return pv_rows,uv_rows,total_pv,total_uv,available_since
        pv_rows,uv_rows,total_pv,total_uv,available_since=use_analytics_database(read_hourly)
        current_hour=current.strftime('%Y-%m-%dT%H')
        hours=[]
        for value in range(24):
            key=f'{day}T{value:02d}'
            available=bool(available_since and key>=available_since and key<=current_hour)
            hours.append({'hour':f'{value:02d}:00','pv':pv_rows.get(key,0) if available else None,'uv':uv_rows.get(key,0) if available else None})
        return {
            'date':day,
            'timezone':'Asia/Shanghai',
            'retentionDays':90,
            'availableSince':f'{available_since}:00:00+08:00' if available_since else None,
            'totals':{'pv':total_pv,'uv':total_uv},
            'hours':hours,
            'updatedAt':current.isoformat(timespec='seconds'),
        }

    @app.get('/auth/login')
    async def login(request: Request, return_to: str = '#home'):
        if not enabled: raise HTTPException(503,'魔搭登录尚未配置')
        # Only a local chapter/home hash can be used as the return destination.
        import re
        request.session['return_to'] = return_to if re.fullmatch(r'#[a-zA-Z0-9_/?=&%-]{1,180}', return_to) else '#home'
        return await oauth.modelscope.authorize_redirect(request, base+'/auth/callback')

    @app.get('/auth/callback')
    async def callback(request: Request):
        if not enabled: raise HTTPException(503,'魔搭登录尚未配置')
        try:
            token = await oauth.modelscope.authorize_access_token(request)
            info = token.get('userinfo')
            if not info or not info.get('sub'): raise ValueError('Missing validated identity')
        except (OAuthError, ValueError):
            return RedirectResponse('/?login=failed#home',status_code=303)
        sub=str(info['sub'])
        name=str(info.get('name') or info.get('preferred_username') or '魔搭读者')[:100]
        now=int(time.time()); sid=secrets.token_urlsafe(32)
        with db() as conn:
            conn.execute('INSERT INTO users VALUES (?,?,?) ON CONFLICT(sub) DO UPDATE SET name=excluded.name',(secrets.token_hex(16),sub,name))
            uid=conn.execute('SELECT id FROM users WHERE sub=?',(sub,)).fetchone()['id']
            conn.execute('DELETE FROM sessions WHERE expires<=? OR id=?',(now,request.session.get('sid','')))
            conn.execute('INSERT INTO sessions VALUES (?,?,?)',(sid,uid,now+7*86400))
        target=request.session.get('return_to','#home')
        request.session.clear()
        request.session.update(sid=sid,csrf=secrets.token_urlsafe(32))
        return RedirectResponse('/'+target,status_code=303)

    @app.post('/api/logout')
    def logout(request: Request):
        require_user(request)
        with db() as conn: conn.execute('DELETE FROM sessions WHERE id=?',(request.session.get('sid'),))
        request.session.clear()
        return {'ok':True}

    @app.get('/api/chapters/{chapter}/entries')
    def list_entries(chapter: str, request: Request, before: int = 0):
        storage_chapter=check_chapter(chapter); u=user(request); uid=u['id'] if u else ''
        # Rowid cursor remains stable even when multiple entries share a timestamp.
        with db() as conn:
            rows=conn.execute('SELECT e.rowid cursor,e.*,u.name FROM entries e JOIN users u ON u.id=e.user_id WHERE e.chapter=? AND (e.kind!=\'highlight\' OR e.user_id=?) AND (?=0 OR e.rowid<?) ORDER BY e.rowid DESC LIMIT 101',(storage_chapter,uid,before,before)).fetchall()
        items=[]
        for row in rows[:100]:
            item=dict(row); item['chapter']=chapter; item['mine']=item['user_id']==uid
            item['canDelete']=item['mine'] or bool(u and u['sub'] in admins)
            item.pop('user_id'); items.append(item)
        return {'items':items,'next':items[-1]['cursor'] if len(rows)>100 else None}

    @app.post('/api/chapters/{chapter}/entries',status_code=201)
    def add_entry(chapter: str, entry: Entry, request: Request):
        u=require_user(request); chapter=check_chapter(chapter)
        if entry.kind not in ('highlight','annotation','comment'): raise HTTPException(422,'不支持的笔记类型')
        if entry.kind!='highlight' and not entry.text.strip(): raise HTTPException(422,'请填写内容')
        if entry.kind!='comment' and (not entry.quote.strip() or entry.end<=entry.start): raise HTTPException(422,'请先选择正文中的文字')
        now=int(time.time()); eid=secrets.token_hex(16)
        with db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            count=conn.execute('SELECT count(*) FROM entries WHERE user_id=? AND created>?',(u['id'],now-60)).fetchone()[0]
            if count>=10: raise HTTPException(429,'操作太频繁，请稍后再试')
            if entry.kind=='highlight':
                existing=conn.execute('SELECT id FROM entries WHERE chapter=? AND user_id=? AND kind=? AND block=? AND start=? AND end=? AND quote=?',(chapter,u['id'],entry.kind,entry.block,entry.start,entry.end,entry.quote)).fetchone()
                if existing: return {'id':existing['id']}
            conn.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)',(eid,chapter,u['id'],entry.kind,entry.text.strip(),entry.quote,entry.block,entry.start,entry.end,now))
        return {'id':eid}

    @app.delete('/api/entries/{entry_id}')
    def delete_entry(entry_id: str, request: Request):
        u=require_user(request)
        with db() as conn:
            row=conn.execute('SELECT user_id FROM entries WHERE id=?',(entry_id,)).fetchone()
            if not row: raise HTTPException(404,'内容已删除')
            if row['user_id']!=u['id'] and u['sub'] not in admins: raise HTTPException(403,'只能删除自己发表的内容')
            conn.execute('DELETE FROM entries WHERE id=?',(entry_id,))
        return {'ok':True}

    @app.get('/api/wishes')
    def list_wishes(request: Request, before: int = 0):
        u=user(request)
        with db() as conn:
            rows=conn.execute('SELECT w.rowid cursor,w.*,u.name FROM wishes w JOIN users u ON u.id=w.user_id WHERE (?=0 OR w.rowid<?) ORDER BY w.rowid DESC LIMIT 21',(before,before)).fetchall()
        items=[]
        for row in rows[:20]:
            item=dict(row)
            item['canDelete']=bool(u and (item['user_id']==u['id'] or u['sub'] in admins))
            item.pop('user_id'); items.append(item)
        return {'items':items,'next':items[-1]['cursor'] if len(rows)>20 else None}

    @app.post('/api/wishes',status_code=201)
    def add_wish(wish: Wish, request: Request):
        u=require_user(request)
        text=wish.text.strip()
        if not text: raise HTTPException(422,'请写下希望补充的内容')
        now=int(time.time()); wid=secrets.token_hex(16)
        with db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            count=conn.execute('SELECT count(*) FROM wishes WHERE user_id=? AND created>?',(u['id'],now-60)).fetchone()[0]
            if count>=5: raise HTTPException(429,'愿望发送太频繁，请稍后再试')
            conn.execute('INSERT INTO wishes VALUES (?,?,?,?)',(wid,u['id'],text,now))
        return {'id':wid}

    @app.delete('/api/wishes/{wish_id}')
    def delete_wish(wish_id: str, request: Request):
        u=require_user(request)
        with db() as conn:
            row=conn.execute('SELECT user_id FROM wishes WHERE id=?',(wish_id,)).fetchone()
            if not row: raise HTTPException(404,'这条愿望已删除')
            if row['user_id']!=u['id'] and u['sub'] not in admins: raise HTTPException(403,'只能删除自己发表的愿望')
            conn.execute('DELETE FROM wishes WHERE id=?',(wish_id,))
        return {'ok':True}

    @app.get('/')
    def index(): return FileResponse(ROOT/'index.html',headers={'Cache-Control':'no-cache'})
    @app.get('/analytics')
    def analytics_page(): return FileResponse(ROOT/'assets/analytics.html',headers={'Cache-Control':'no-store'})
    @app.get('/favicon.svg')
    def favicon(): return FileResponse(ROOT/'favicon.svg')
    @app.get('/deployment.json')
    def deployment():
        if not (ROOT/'deployment.json').exists(): raise HTTPException(404)
        return FileResponse(ROOT/'deployment.json')
    for directory in ('assets','content','chapters'):
        app.mount('/'+directory,StaticFiles(directory=ROOT/directory),name=directory)
    for filename in ('CONTRIBUTING.md','README.md','README.zh-CN.md','LICENSE'):
        def make_document(path):
            def document(): return FileResponse(path)
            return document
        app.add_api_route('/'+filename,make_document(ROOT/filename),methods=['GET'])

    app.state.db=db
    app.state.analytics_db=analytics_db
    app.state.analytics_path=analytics_path
    app.state.persistent_analytics_path=persistent_analytics_path
    app.state.snapshot_analytics=snapshot_analytics_database
    app.state.oauth=oauth
    return app

app=create_app()
