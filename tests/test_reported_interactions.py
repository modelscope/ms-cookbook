import json
from unittest.mock import AsyncMock
import httpx
from fastapi.testclient import TestClient
from app import create_app
from pathlib import Path
from test_discussion import reader,site,ENDPOINT

def test_existing_reader_comments_have_clickable_profile(site):
    client=reader(site,'legacy-reader')
    client.post(ENDPOINT,json={'kind':'comment','text':'已有读者的留言'})
    item=client.get(ENDPOINT).json()['items'][0]
    assert item['profileUrl'], 'Existing comments render a strong element instead of a profile link'

def test_chapter_23_video_links_play_instead_of_download():
    data=json.loads((Path(__file__).resolve().parents[1]/'assets/content.js').read_text().removeprefix('window.BOOK_DATA = ').removesuffix(';\n'))
    chapter=next(c for c in data['chapters'] if c['number']==23)
    assert '<video' in chapter['html'], 'Videos are download-only attachments without a player'
    assert chapter['html'].count('<video')==5
    assert 'download=' not in chapter['html']

def test_legacy_handle_opens_verified_profile_and_is_backfilled(site):
    client=reader(site,'fanxiansheng00')
    site[0].state.lookup_profile=lambda name:name if name=='fanxiansheng00' else None
    client.post(ENDPOINT,json={'kind':'comment','text':'旧留言'})
    item=client.get(ENDPOINT).json()['items'][0]
    result=client.get(item['profileUrl'],follow_redirects=False)
    assert result.status_code==303
    assert result.headers['location']=='https://modelscope.cn/profile/fanxiansheng00'
    assert client.get(ENDPOINT).json()['items'][0]['profileUrl']==result.headers['location']

def test_live_comment_total_excludes_private_highlights(site):
    client=reader(site)
    summary='/api/community/summary'
    assert client.get(summary).json()['comments']==0
    parent=client.post(ENDPOINT,json={'kind':'comment','text':'留言'}).json()['id']
    client.post(ENDPOINT,json={'kind':'comment','text':'回复','parentId':parent})
    client.post(ENDPOINT,json={'kind':'annotation','text':'想法','quote':'hello','end':5})
    client.post(ENDPOINT,json={'kind':'highlight','quote':'hello','end':5})
    client.post('/api/wishes',json={'text':'愿望单独统计'})
    assert client.get(summary).json()['comments']==3
    assert client.get(summary).headers['cache-control']=='no-store'
    client.delete('/api/entries/'+parent)
    assert client.get(summary).json()['comments']==2

def test_oauth_handle_can_be_obtained_from_official_openapi(site,monkeypatch):
    monkeypatch.setenv('OAUTH_CLIENT_ID','test-client');monkeypatch.setenv('OAUTH_CLIENT_SECRET','test-secret')
    app=create_app(site[1]);provider=app.state.oauth.modelscope
    provider.authorize_access_token=AsyncMock(return_value={'userinfo':{'sub':'fan-sub','name':'fanxiansheng00'},'access_token':'test-only'})
    provider.userinfo=AsyncMock(return_value={'sub':'fan-sub','name':'fanxiansheng00'})
    provider.get=AsyncMock(return_value=httpx.Response(200,json={'success':True,'data':{'username':'fanxiansheng00'}},request=httpx.Request('GET','https://modelscope.cn/openapi/v1/users/me')))
    client=TestClient(app,base_url='http://127.0.0.1:7860')
    assert client.get('/auth/callback',follow_redirects=False).status_code==303
    assert client.get('/api/session').json()['user']['profileUrl']=='https://modelscope.cn/profile/fanxiansheng00'
