import datetime
import threading

from api.webmonitor import constants,site_status,utils
from api.webmonitor.producer import Producer
import time,re
from api import db


def verify_domains(producer: Producer):
    while True:
        urls = producer.consume(count=2)
        if urls is None:
            print(f"{datetime.now()}: SLEEPING Thread ID::{threading.get_ident()}")
            time.sleep(10)
            continue
        for url in urls:
            try:
                true_domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, "", url['site_name'])
                index_domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, "", url['index_page'])
                request_url = url['index_page'] if true_domain.split(".")[0] != index_domain.split(".")[0] \
                    else url['site_name']

                check_result = site_status.check_site(request_url)
                if check_result is None:
                    print(f"{utils.current_time()}: {url} check_site returned None")
                    continue

                check_result["page_recent_check"] = utils.current_time()

                db.update_domain_status(domain_name=url['site_name'], obj=check_result)

                #if url["priority"] == 5 and url["site_status"] == "active" and check_result["site_status"] != "active":
                    #utils.send_exchange_email_rest_simple(
                     #   recipients=[ "r.neretse@ncsa.gov.rw", "b.nzamwita@ncsa.gov.rw"],
                     #   subject="Critical Website Down", body=site_down_email_body(domain=url["site_name"],
                     #                                                              href=request_url))
            except Exception as e:
                print(f"error: {e}")
                print(f"Error from defacement check : {repr(e)}", True)
