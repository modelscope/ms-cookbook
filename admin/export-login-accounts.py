"""Export successful Purplebook login identities for matching ModelScope registrations."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import sqlite3
import sys
from zoneinfo import ZoneInfo


def export_accounts(database, output):
    # A read-only connection prevents an incorrect path from creating a new DB.
    with sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True) as conn:
        conn.row_factory=sqlite3.Row
        rows=conn.execute('''SELECT u.id,u.sub,p.username,
            MIN(l.first_login) first_login,MAX(l.last_login) last_login,
            COALESCE(SUM(l.login_count),0) login_count
            FROM users u LEFT JOIN user_profiles p ON p.user_id=u.id
            LEFT JOIN account_login_daily l ON l.user_id=u.id
            GROUP BY u.id,u.sub,p.username ORDER BY first_login,u.id''')
        writer=csv.writer(output)
        writer.writerow(['purplebook_user_id','modelscope_sub','modelscope_username',
                         'first_recorded_login_at','last_recorded_login_at','recorded_login_count'])
        for row in rows:
            def timestamp(value):
                return datetime.fromtimestamp(value,ZoneInfo('Asia/Shanghai')).isoformat() if value is not None else ''
            writer.writerow([spreadsheet_text(row['id']),spreadsheet_text(row['sub']),spreadsheet_text(row['username'] or ''),
                             timestamp(row['first_login']),timestamp(row['last_login']),row['login_count']])


def spreadsheet_text(value):
    # Account handles are external text; keep spreadsheet programs from evaluating it.
    return "'"+value if value.startswith(('=','+','-','@','\t','\r','\n')) else value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True,help='Path to reading.sqlite3')
    args=parser.parse_args()
    export_accounts(args.database,sys.stdout)
