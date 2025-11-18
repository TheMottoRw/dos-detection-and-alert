from datetime import datetime, timedelta
from flask import jsonify

from ..db import (
    get_websites_collection,
    get_keyword_collection,
    get_log_collection,
)


def get_dashboard_stats():
    """Return aggregated stats for dashboard in JSON.

    Includes:
    - total_websites
    - active_websites
    - defaced_websites
    - total_keywords
    - recent_logs_7d (ban/unban related)
    """

    websites = get_websites_collection()
    keywords = get_keyword_collection()
    logs = get_log_collection()

    # Websites counts
    total_websites = websites.count_documents({})
    active_websites = websites.count_documents({"site_status": "active"})

    # Defaced can be represented either via site_status or defacement_status
    defaced_websites = websites.count_documents({
        "$or": [
            {"site_status": "defaced"},
            {"defacement_status": "defaced"},
        ]
    })

    # Keywords count
    total_keywords = keywords.count_documents({})

    # Recent logs (7 days) related to banning/unbanning
    since = datetime.now() - timedelta(days=90)
    ban_actions = [
        "ban",
        "banned",
        "banning",
        "unban",
        "unbanned",
        "unbanning",
    ]
    recent_logs_7d = logs.count_documents({
        "action": {"$in": ban_actions},
        "createdAt": {"$gte": since},
    })

    return jsonify({
        "total_websites": total_websites,
        "active_websites": active_websites,
        "defaced_websites": defaced_websites,
        "total_keywords": total_keywords,
        "recent_logs_7d": recent_logs_7d,
    }), 200
