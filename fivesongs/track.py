from datetime import datetime

from flask import abort
from user_agents import parse

from fivesongs.db import get_db

def capture(user_agent):
    user_agent_parsed = parse(user_agent)
    simple_tracking(user_agent_parsed)
    disallowed = ['AhrefsBot 7.0', 'BacklinksExtendedBot', 'Inventory Crawler', 'domainsbot', 'SeznamBot 4.0', 'SERankingBacklinksBot 1.0', 'domains-monitor-bot 1.0', 'serpstatbot 2.1', 'OAI-SearchBot 1.3', 'DataForSeoBot 1.0']
    if user_agent_parsed.get_browser() in disallowed:
        abort(401)
    if user_agent_parsed.ua_string == 'http://5songsdaily.com/wordpress/wp-admin/setup-config.php':
        abort(401)

def simple_tracking(user_agent_parsed):
    insert_query = ("INSERT INTO track (ua, device, os, browser, is_bot, is_email_client, is_mobile, is_pc, is_tablet, is_touch_capable, request_date) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                    "RETURNING id;")
    try:
        db = get_db()
        track_insert = db.execute(insert_query, (
            user_agent_parsed.ua_string,
            str(user_agent_parsed.device),
            user_agent_parsed.get_os(),
            user_agent_parsed.get_browser(),
            user_agent_parsed.is_bot,
            user_agent_parsed.is_email_client,
            user_agent_parsed.is_mobile,
            user_agent_parsed.is_pc,
            user_agent_parsed.is_tablet,
            user_agent_parsed.is_touch_capable,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )).fetchone()
        ua_id = track_insert['id']
        db.commit()
    except Exception as e:
        print(e)
