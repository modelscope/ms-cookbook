import base64
import json
import time
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from app import create_app

@pytest.fixture
def site(tmp_path,monkeypatch):
    monkeypatch.setenv('APP_BASE_URL','http://127.0.0.1:7860')
    monkeypatch.delenv('OAUTH_CLIENT_ID',raising=False)
    monkeypatch.delenv('OAUTH_CLIENT_SECRET',raising=False)
    return create_app(tmp_path),tmp_path

def reader(site,uid='alice'):
    app,path=site
    with app.state.db() as db:
        db.execute('INSERT OR IGNORE INTO users VALUES (?,?,?)',(uid,'sub-'+uid,uid))
        db.execute('INSERT OR REPLACE INTO sessions VALUES (?,?,?)',('session-'+uid,uid,int(time.time())+1000))
    c=TestClient(app,base_url='http://127.0.0.1:7860')
    data=base64.b64encode(json.dumps({'sid':'session-'+uid,'csrf':'test-csrf'}).encode())
    cookie=TimestampSigner((path/'session.key').read_text()).sign(data).decode()
    c.cookies.set('purplebook_session',cookie)
    c.headers.update({'origin':'http://127.0.0.1:7860','x-csrf-token':'test-csrf'})
    return c

ENDPOINT='/api/chapters/chapter-1/entries'

def test_renumbering_keeps_notes_with_original_article(site):
    c=reader(site)
    with site[0].state.db() as db:
        for eid,chapter,kind in [('case','chapter-20','comment'),('agent','chapter-33','annotation'),('private','chapter-20','highlight')]:
            db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)',(eid,chapter,'alice',kind,eid,'original quote',1,0,14,10))
    case='/api/chapters/chapter-23/entries'
    agent='/api/chapters/chapter-29/entries'
    assert {x['id'] for x in c.get(case).json()['items']}=={'case','private'}
    assert c.get(agent).json()['items'][0]['id']=='agent'
    assert c.get(agent).json()['items'][0]['chapter']=='chapter-29'
    assert c.get('/api/chapters/chapter-22/entries').json()['items']==[]
    assert c.get('/api/chapters/chapter-36/entries').json()['items']==[]
    assert c.get('/api/chapters/chapter-26/entries').json()['items']==[]
    assert c.get('/api/chapters/chapter-27/entries').status_code==404
    guest=TestClient(site[0])
    assert {x['id'] for x in guest.get(case).json()['items']}=={'case'}
    response=c.post(agent,json={'kind':'comment','text':'new comment'})
    assert response.status_code==201
    with site[0].state.db() as db:
        assert db.execute('SELECT chapter FROM entries WHERE id=?',(response.json()['id'],)).fetchone()['chapter']=='chapter-33'
    restarted=reader((create_app(site[1]),site[1]))
    assert {x['text'] for x in restarted.get(agent).json()['items']}=={'agent','new comment'}

def test_auth_and_csrf(site):
    guest=TestClient(site[0]); assert guest.post(ENDPOINT,json={'kind':'comment','text':'hi'}).status_code==401
    c=reader(site); c.headers['origin']='https://evil.example'
    assert c.post(ENDPOINT,json={'kind':'comment','text':'hi'}).status_code==403
    c.headers['origin']='http://127.0.0.1:7860';c.headers['x-csrf-token']='wrong'
    assert c.post(ENDPOINT,json={'kind':'comment','text':'hi'}).status_code==403

def test_visibility_ownership_and_restart(site):
    c=reader(site);b=reader(site,'bob');guest=TestClient(site[0])
    private=c.post(ENDPOINT,json={'kind':'highlight','quote':'hello','block':0,'start':0,'end':5}).json()['id']
    public=c.post(ENDPOINT,json={'kind':'annotation','quote':'hello','block':0,'start':0,'end':5,'text':'idea'}).json()['id']
    assert len(c.get(ENDPOINT).json()['items'])==2
    assert [i['id'] for i in b.get(ENDPOINT).json()['items']]==[public]
    assert [i['id'] for i in guest.get(ENDPOINT).json()['items']]==[public]
    assert b.delete('/api/entries/'+public).status_code==403
    assert b.delete('/api/entries/'+private).status_code==403
    assert TestClient(create_app(site[1])).get(ENDPOINT).json()['items'][0]['id']==public
    assert c.delete('/api/entries/'+public).status_code==200
    assert guest.get(ENDPOINT).json()['items']==[]

def test_validation_chapters_and_rate_limit(site):
    c=reader(site)
    for body in [{'kind':'invalid'},{'kind':'comment','text':' '},{'kind':'annotation','text':'x'},{'kind':'comment','text':'x'*2001}]:
        assert c.post(ENDPOINT,json=body).status_code==422
    assert c.post('/api/chapters/chapter-999/entries',json={'kind':'comment','text':'x'}).status_code==404
    for i in range(10): assert c.post(ENDPOINT,json={'kind':'comment','text':str(i)}).status_code==201
    assert c.post(ENDPOINT,json={'kind':'comment','text':'rate'}).status_code==429
    assert c.get('/api/chapters/chapter-2/entries').json()['items']==[]

def test_logout_revokes_session(site):
    c=reader(site);old=c.cookies.get('purplebook_session')
    assert c.post('/api/logout').status_code==200
    c.cookies.clear();c.cookies.set('purplebook_session',old)
    assert c.get('/api/session').json()['user'] is None

def test_static_files_do_not_expose_database_or_source(site):
    c=TestClient(site[0])
    for path in ['/app.py','/.data/session.key','/tests/test_discussion.py','/.git/config','/assets/../app.py']:
        assert c.get(path).status_code==404
    assert 'Apache' in c.get('/LICENSE?path=/etc/passwd').text
    assert c.get('/api/session').headers['cache-control']=='no-store'
    assert c.get('/auth/login').status_code==503

def test_oauth_validated_identity_and_return_path(site,monkeypatch):
    monkeypatch.setenv('OAUTH_CLIENT_ID','test-client');monkeypatch.setenv('OAUTH_CLIENT_SECRET','test-secret')
    app=create_app(site[1]); c=TestClient(app,base_url='http://127.0.0.1:7860')
    # Only replace the external provider exchange; no test login endpoint exists.
    app.state.oauth.modelscope.authorize_access_token=AsyncMock(return_value={'userinfo':{'sub':'provider-sub','name':'测试读者','preferred_username':'test-reader'},'access_token':'never-store-this'})
    r=c.get('/auth/callback',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/#home'
    state=c.get('/api/session').json();assert state['user']['name']=='测试读者'
    assert state['user']['profileUrl']=='https://modelscope.cn/profile/test-reader'
    assert 'provider-sub' not in r.headers['set-cookie'] and 'never-store-this' not in r.headers['set-cookie']
    assert state['csrf']

def test_profile_from_userinfo_and_subject_binding(site,monkeypatch):
    monkeypatch.setenv('OAUTH_CLIENT_ID','test-client');monkeypatch.setenv('OAUTH_CLIENT_SECRET','test-secret')
    app=create_app(site[1]);c=TestClient(app,base_url='http://127.0.0.1:7860')
    provider=app.state.oauth.modelscope
    provider.authorize_access_token=AsyncMock(return_value={'userinfo':{'sub':'stable-sub','name':'昵称不是用户名'},'access_token':'secret'})
    provider.userinfo=AsyncMock(return_value={'sub':'stable-sub','preferred_username':'real-handle'})
    assert c.get('/auth/callback',follow_redirects=False).status_code==303
    state=c.get('/api/session').json()
    c.headers.update({'origin':'http://127.0.0.1:7860','x-csrf-token':state['csrf']})
    c.post(ENDPOINT,json={'kind':'comment','text':'我的评论'})
    c.post('/api/wishes',json={'text':'我的愿望'})
    for url in (ENDPOINT,'/api/wishes'):
        item=TestClient(app).get(url).json()['items'][0]
        assert item['profileUrl']=='https://modelscope.cn/profile/real-handle'
        assert 'stable-sub' not in json.dumps(item)
    original_id=state['user']['id']
    provider.userinfo=AsyncMock(return_value={'sub':'stable-sub','preferred_username':'renamed-handle'})
    c.get('/auth/callback',follow_redirects=False)
    assert c.get('/api/session').json()['user']['id']==original_id
    assert TestClient(app).get(ENDPOINT).json()['items'][0]['profileUrl']=='https://modelscope.cn/profile/renamed-handle'
    provider.userinfo=AsyncMock(return_value={'sub':'different-sub','preferred_username':'wrong-person'})
    stranger=TestClient(app)
    assert 'login=failed' in stranger.get('/auth/callback',follow_redirects=False).headers['location']
    assert stranger.get('/api/session').json()['user'] is None

def test_replies_validate_parent_and_preserve_context_after_delete(site):
    alice=reader(site);bob=reader(site,'bob');guest=TestClient(site[0])
    parent=alice.post(ENDPOINT,json={'kind':'comment','text':'原留言'}).json()['id']
    private=alice.post(ENDPOINT,json={'kind':'highlight','quote':'hello','end':5}).json()['id']
    for target in [private,'missing']:
        assert bob.post(ENDPOINT,json={'kind':'comment','text':'回复','parentId':target}).status_code==422
    assert bob.post('/api/chapters/chapter-2/entries',json={'kind':'comment','text':'回复','parentId':parent}).status_code==422
    assert guest.post(ENDPOINT,json={'kind':'comment','text':'回复','parentId':parent}).status_code==401
    reply=bob.post(ENDPOINT,json={'kind':'comment','text':'一条回复','parentId':parent}).json()['id']
    item=guest.get(ENDPOINT).json()['items'][0]
    assert item['replyTo']=={'id':parent,'name':'alice','text':'原留言'}
    restarted=TestClient(create_app(site[1]))
    assert restarted.get(ENDPOINT).json()['items'][0]['id']==reply
    alice.delete('/api/entries/'+parent)
    item=guest.get(ENDPOINT).json()['items'][0]
    assert item['id']==reply and item['replyTo']['id'] is None
    assert bob.delete('/api/entries/'+reply).status_code==200

def test_oauth_rejects_missing_state(site,monkeypatch):
    monkeypatch.setenv('OAUTH_CLIENT_ID','test-client');monkeypatch.setenv('OAUTH_CLIENT_SECRET','test-secret')
    app=create_app(site[1]); c=TestClient(app)
    response=c.get('/auth/callback?code=fake&state=unsolicited',follow_redirects=False)
    assert response.status_code==303 and 'login=failed' in response.headers['location']
    assert c.get('/api/session').json()['user'] is None

def test_pagination_preserves_same_second_entries(site):
    app,_=site;c=reader(site)
    with app.state.db() as db:
        for i in range(105): db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)',(str(i),'chapter-1','alice','comment','test','',0,0,0,10))
    page=c.get(ENDPOINT).json();assert len(page['items'])==100
    second=c.get(ENDPOINT+'?before='+str(page['next'])).json();assert len(second['items'])==5
    assert not {x['id'] for x in page['items']} & {x['id'] for x in second['items']}


def test_wishes_auth_visibility_ownership_and_restart(site):
    guest=TestClient(site[0]);alice=reader(site);bob=reader(site,'bob')
    assert guest.post('/api/wishes',json={'text':'想学习模型部署'}).status_code==401
    alice.headers['x-csrf-token']='wrong'
    assert alice.post('/api/wishes',json={'text':'想学习模型部署'}).status_code==403
    alice.headers['x-csrf-token']='test-csrf'
    wid=alice.post('/api/wishes',json={'text':'  想学习模型部署  '}).json()['id']
    item=guest.get('/api/wishes').json()['items'][0]
    assert item['text']=='想学习模型部署' and item['name']=='alice'
    assert not item['canDelete'] and 'user_id' not in item
    assert alice.get('/api/wishes').json()['items'][0]['canDelete']
    assert bob.delete('/api/wishes/'+wid).status_code==403
    assert guest.delete('/api/wishes/'+wid).status_code==401
    assert TestClient(create_app(site[1])).get('/api/wishes').json()['items'][0]['id']==wid
    assert guest.get(ENDPOINT).json()['items']==[]
    assert alice.delete('/api/wishes/'+wid).status_code==200
    assert guest.get('/api/wishes').json()['items']==[]


def test_wishes_validation_rate_limit_and_pagination(site):
    c=reader(site)
    for body in [{},{'text':' '},{'text':'字'*2001}]:
        assert c.post('/api/wishes',json=body).status_code==422
    for i in range(5):assert c.post('/api/wishes',json={'text':str(i)}).status_code==201
    assert c.post('/api/wishes',json={'text':'too many'}).status_code==429
    with site[0].state.db() as db:
        for i in range(30):db.execute('INSERT INTO wishes VALUES (?,?,?,?)',('wish-'+str(i),'alice','test',10))
    first=c.get('/api/wishes').json();second=c.get('/api/wishes?before='+str(first['next'])).json()
    assert len(first['items'])==20 and len(second['items'])==15 and second['next'] is None
    assert not {i['id'] for i in first['items']} & {i['id'] for i in second['items']}


def test_wishes_moderation(site,monkeypatch):
    monkeypatch.setenv('MODERATOR_SUBS','sub-mod')
    updated=(create_app(site[1]),site[1]);alice=reader(updated);mod=reader(updated,'mod')
    wid=alice.post('/api/wishes',json={'text':'愿望'}).json()['id']
    assert mod.get('/api/wishes').json()['items'][0]['canDelete']
    assert mod.delete('/api/wishes/'+wid).status_code==200
