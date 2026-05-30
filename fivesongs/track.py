from datetime import datetime

from flask import abort
from ua_parser import user_agent_parser

from fivesongs.db import get_db
from fivesongs.disallowed import disallowed_list

def capture(request_headers, request_url):
    user_agent = request_headers.get('User-Agent')
    ua_dict = user_agent_parser.Parse(user_agent)
    ua_dict['referer'] = request_headers.get('Referer')
    ua_dict['request_url'] = request_url
    if ua_dict['user_agent']['family'] in disallowed_list:
        simple_tracking(ua_dict, blocked=True)
        abort(401)
    simple_tracking(ua_dict, blocked=False)

def simple_tracking(ua_dict, blocked):
    print("BLOCKED", blocked)
    insert_query = ("INSERT INTO track (ua, device, os, browser, referer, url, blocked, request_date) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?) "
                    "RETURNING id;")
    try:
        db = get_db()
        track_insert = db.execute(insert_query, (
            ua_dict['string'],
            str(ua_dict['device']),
            str(ua_dict['os']),
            str(ua_dict['user_agent']),
            str(ua_dict['referer']),
            str(ua_dict['request_url']),
            blocked,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )).fetchone()
        ua_id = track_insert['id']
        db.commit()
    except Exception as e:
        print(e)
