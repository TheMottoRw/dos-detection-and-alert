from datetime import datetime
import threading

from . import constants,site_status,utils
from .producer import Producer
import time,re
from api import db


def _load_websites_into_producer(producer: Producer):
    try:
        coll = db.get_websites_collection()
        cursor = coll.find({"site_status":"active"}, {"site_name": 1, "index_page": 1, "site_status": 1})
        items = []
        for doc in cursor:
            site_name = doc.get("site_name")
            if not site_name:
                continue
            index_page = doc.get("index_page") or site_name
            # Give priority to critical systems if configured
            priority = 5 if site_name in getattr(constants, "CRITICAL_SYS", []) else 1
            items.append({
                "site_name": site_name,
                "index_page": index_page,
                "site_status": doc.get("site_status", "unknown"),
                "priority": priority,
            })
        if items:
            total = producer.add(items)
            print(f"{datetime.now()}: Loaded {len(items)} website(s) from DB into queue. Queue size: {total}")
            return True
        else:
            print(f"{datetime.now()}: No websites found in DB to enqueue.")
            return False
    except Exception as e:
        print(f"{datetime.now()}: Error loading websites into producer: {e}")
        return False


def verify_domains(producer: Producer):
    while True:
        urls = producer.consume(count=2)
        if urls is None:
            # Queue empty: try to load from DB Websites collection
            loaded = _load_websites_into_producer(producer)
            urls = loaded
            if not loaded:
                print(f"{datetime.now()}: SLEEPING Thread ID::{threading.get_ident()}")
                time.sleep(10)
            continue
        # Get keywords from database
        keywords_collection = db.get_keyword_collection()
        keywords = [kw['name'] for kw in keywords_collection.find({}, {'name': 1})]

        for url in urls:
            try:
                true_domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, "", url['site_name'])
                index_domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, "", url['index_page'])
                request_url = url['index_page'] if true_domain.split(".")[0] != index_domain.split(".")[0] \
                    else url['site_name']

                check_result = site_status.check_site(request_url)
                print(check_result['url']," ",check_result['site_status'])
                if check_result is None:
                    print(f"{utils.current_time()}: {url} check_site returned None")
                    continue

                if check_result["site_status"] == "active" and check_result.get("current_content"):
                    for keyword in keywords:
                        if keyword.lower() in check_result["current_content"].lower():
                            check_result["site_status"] = "defaced"
                            print(f"{utils.current_time()}: {url} defaced")
                            break

                check_result["page_recent_check"] = utils.current_time()

                # db.update_domain_status(domain_name=url['site_name'], obj=check_result)
                coll = db.get_websites_collection()
                res = coll.update_one({"site_name": url['site_name']}, {"$set": check_result})

                #if url["priority"] == 5 and url["site_status"] == "active" and check_result["site_status"] != "active":
                    #utils.send_exchange_email_rest_simple(
                     #   recipients=[ "r.neretse@ncsa.gov.rw", "b.nzamwita@ncsa.gov.rw"],
                     #   subject="Critical Website Down", body=site_down_email_body(domain=url["site_name"],
                     #                                                              href=request_url))
            except Exception as e:
                print(f"error: {e}")
                print(f"Error from defacement check : {repr(e)}", True)
