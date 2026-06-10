from datetime import datetime
import sys

from flask import abort
from ua_parser import user_agent_parser

from fivesongs.db import get_db
from fivesongs.extensions import cache

def capture(request_headers, request_url):
    user_agent = request_headers.get('User-Agent', '')
    ua_dict = user_agent_parser.Parse(user_agent)
    ua_dict['referer'] = request_headers.get('Referer')

    if request_headers.getlist("X-Forwarded-For"):
       ip = request_headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request_headers.environ.get('REMOTE_ADDR')
    ua_dict['remote_addr'] = ip

    ua_dict['request_url'] = request_url

    d_agents, d_strs, d_paths, d_ips = get_disallowed()

    blocked = (
        ua_dict['user_agent']['family'] in d_agents or
        any(b in ua_dict['string'] for b in d_strs) or
        any(b in ua_dict['request_url'] for b in d_paths) or
        ua_dict['remote_addr'] in d_ips
    )
    simple_tracking(ua_dict, blocked=blocked)
    if blocked:
        abort(401)

@cache.cached(timeout=1200, key_prefix='blocklist')
def get_disallowed():
    db = get_db()
    disallowed_request = db.execute("SELECT value, block_type FROM blocklist", ()).fetchall()

    # Blocked agents
    disallowed_agents = [d['value'] for d in disallowed_request if d['block_type'] == 'ua_agent']
    # In some cases, I've seen User-Agent strings that contain substrings like `wp-admin`
    disallowed_strs = [d['value'] for d in disallowed_request if d['block_type'] == 'ua_string']
    # Sometimes I want to block on substrings that show up in invalid, probing request urls
    disallowed_paths = [d['value'] for d in disallowed_request if d['block_type'] == 'path']
    # This allows us to block malicious traffi from specific IPs:
    disallowed_ips = [d['value'] for d in disallowed_request if d['block_type'] == 'ip']
    return disallowed_agents, disallowed_strs, disallowed_paths, disallowed_ips

def simple_tracking(ua_dict, blocked):
    insert_query = ("INSERT INTO track (ua, device, os, browser, referer, url, remote_addr, blocked, request_date) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) "
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
            str(ua_dict['remote_addr']),
            blocked,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )).fetchone()
        ua_id = track_insert['id']
        db.commit()
    except Exception as e:
        print(e)
