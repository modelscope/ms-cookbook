import csv
from datetime import datetime, timedelta
import importlib.util
import io
from pathlib import Path
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app import create_app


@pytest.fixture
def login_site(tmp_path,monkeypatch):
    monkeypatch.setenv('APP_BASE_URL','http://127.0.0.1:7860')
    monkeypatch.setenv('OAUTH_CLIENT_ID','test-client')
    monkeypatch.setenv('OAUTH_CLIENT_SECRET','test-secret')
    app=create_app(tmp_path)
    app.state.oauth.modelscope.authorize_access_token=AsyncMock(return_value={
        'userinfo':{'sub':'modelscope-123','name':'读者','preferred_username':'reader'}})
    return app,TestClient(app,base_url='http://127.0.0.1:7860'),tmp_path


def test_login_without_comment_is_counted_and_repeated_logins_are_deduplicated(login_site):
    app,client,_=login_site
    assert client.get('/api/analytics/accounts').json()['total']==0
    for _ in range(2):
        assert client.get('/auth/callback',follow_redirects=False).status_code==303
    for _ in range(3):
        client.get('/api/session')
    summary=client.get('/api/analytics/accounts').json()
    assert (summary['total'],summary['today'],summary['selected'])==(1,1,1)
    with app.state.db() as db:
        row=db.execute('SELECT * FROM account_login_daily').fetchone()
        assert row['login_count']==2
        assert row['first_login']<=row['last_login']
        assert db.execute('SELECT COUNT(*) FROM entries').fetchone()[0]==0
    assert 'modelscope-123' not in str(summary) and 'reader' not in str(summary)


def test_failed_or_cancelled_login_does_not_add_accounts(login_site):
    app,client,_=login_site
    # The real provider rejects missing/invalid OAuth state before saving an identity.
    del app.state.oauth.modelscope.authorize_access_token
    response=client.get('/auth/callback?error=access_denied',follow_redirects=False)
    assert 'login=failed' in response.headers['location']
    assert client.get('/api/analytics/accounts').json()['total']==0


def test_legacy_accounts_keep_unknown_login_dates_and_survive_restart(login_site):
    app,client,path=login_site
    with app.state.db() as db:
        db.execute('INSERT INTO users VALUES (?,?,?)',('old','old-sub','历史读者'))
    summary=client.get('/api/analytics/accounts').json()
    assert summary['total']==1 and summary['today']==summary['selected']==0
    assert summary['trackedSince'] is None
    client.get('/auth/callback',follow_redirects=False)
    restarted=TestClient(create_app(path))
    summary=restarted.get('/api/analytics/accounts').json()
    assert summary['total']==2 and summary['today']==summary['selected']==1


def test_date_range_counts_each_account_once_across_days(login_site):
    app,client,_=login_site
    client.get('/auth/callback',follow_redirects=False)
    today=datetime.now(ZoneInfo('Asia/Shanghai')).date()
    yesterday=(today-timedelta(days=1)).isoformat()
    with app.state.db() as db:
        uid=db.execute('SELECT id FROM users').fetchone()[0]
        db.execute('INSERT INTO users VALUES (?,?,?)',('second','second-sub','另一个账号'))
        for user_id in (uid,'second'):
            db.execute('INSERT INTO account_login_daily VALUES (?,?,?,?,?)',(user_id,yesterday,1,2,3))
    assert client.get('/api/analytics/accounts?days=2').json()['selected']==2
    summary=client.get(f'/api/analytics/accounts?start={today}&end={today}').json()
    assert summary['selected']==summary['today']==1
    assert summary['range']['timezone']=='Asia/Shanghai'
    assert client.get('/api/analytics/accounts?days=0').status_code==422
    assert client.get('/api/analytics/accounts?start=bad&end=bad').status_code==422


def test_upgrade_existing_database_preserves_accounts_without_fabricated_dates(login_site):
    app,_,path=login_site
    with app.state.db() as db:
        db.execute('INSERT INTO users VALUES (?,?,?)',('legacy','legacy-sub','已有账号'))
        db.execute('DROP TABLE account_login_daily')
    upgraded=TestClient(create_app(path))
    summary=upgraded.get('/api/analytics/accounts').json()
    assert summary['total']==1
    assert summary['selected']==summary['today']==0
    assert summary['trackedSince'] is None


def test_export_has_one_row_per_identity_and_no_invented_registration_date(login_site):
    app,client,path=login_site
    client.get('/auth/callback',follow_redirects=False)
    client.get('/auth/callback',follow_redirects=False)
    with app.state.db() as db:
        db.execute('INSERT INTO users VALUES (?,?,?)',('old','old-sub','历史读者'))
        db.execute('INSERT INTO user_profiles VALUES (?,?)',('old','=formula'))
    spec=importlib.util.spec_from_file_location('export_accounts',Path(__file__).resolve().parents[1]/'admin/export-login-accounts.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output=io.StringIO();module.export_accounts(path/'reading.sqlite3',output)
    rows=list(csv.DictReader(io.StringIO(output.getvalue())))
    assert len(rows)==2
    by_sub={row['modelscope_sub']:row for row in rows}
    assert by_sub['modelscope-123']['recorded_login_count']=='2'
    assert by_sub['modelscope-123']['first_recorded_login_at'].endswith('+08:00')
    assert by_sub['old-sub']['first_recorded_login_at']==''
    assert by_sub['old-sub']['recorded_login_count']=='0'
    assert by_sub['old-sub']['modelscope_username']=="'=formula"
    assert not any('registered' in key for key in rows[0])


def test_analytics_page_has_account_metrics(login_site):
    _,client,_=login_site
    page=client.get('/analytics').text
    assert 'id="accountTotal"' in page and 'id="accountSelected"' in page
    assert client.get('/api/analytics/accounts').headers['cache-control']=='no-store'
    assert client.get('/admin/export-login-accounts.py').status_code==404
