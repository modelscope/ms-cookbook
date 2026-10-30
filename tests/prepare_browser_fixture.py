"""Isolated browser-test state; never imported by the application."""
import base64
import json
import os
import time
from pathlib import Path
from itsdangerous import TimestampSigner
from app import create_app

app=create_app()
with app.state.db() as db:
    db.execute('INSERT INTO users VALUES (?,?,?)',('browser-reader','test-sub','测试读者'))
    db.execute('INSERT INTO user_profiles VALUES (?,?)',('browser-reader','test-reader'))
    db.execute('INSERT INTO users VALUES (?,?,?)',('legacy-fan','old-sub','fanxiansheng00'))
    db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)',('legacy-message','chapter-2','legacy-fan','comment','旧账号主页验证','',0,0,0,10))
    db.execute('INSERT INTO sessions VALUES (?,?,?)',('browser-session','browser-reader',int(time.time())+600))
payload=base64.b64encode(json.dumps({'sid':'browser-session','csrf':'browser-csrf'}).encode())
cookie=TimestampSigner((Path(os.environ['DATA_DIR'])/'session.key').read_text()).sign(payload).decode()
(Path(os.environ['DATA_DIR'])/'browser-cookie.json').write_text(json.dumps(cookie))
