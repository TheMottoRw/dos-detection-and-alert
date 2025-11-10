import math
import time

import requests
import re
import sys
import subprocess
import json

# from bs4 import BeautifulSoup
from requests.exceptions import TooManyRedirects
from urllib3.exceptions import MaxRetryError, ConnectionError

from . import constants, utils, syscmd
from .. import db
# import db, constants, utils, syscmd

# from cryptography import x509
import socket
from difflib import SequenceMatcher

def is_hacked(url=None, protocol='https', content=None,
              current_content=None, domain=None):
    # str_pattern (regex|regex)
    str_pattern = db.load_defacement_keywords_names()['pattern']
    url_address = f"{protocol}://{url}"
    try:
        if url:
            res = utils.load_url(url, protocol=protocol, timeout=180)
            content = res['content']
            return check_defacement_content_changes(str_pattern, current_content, content)
        elif content:
            conteChanges = check_defacement_content_changes(str_pattern, current_content, content)
            # print(f"Content changes:: {conteChanges}")
            return conteChanges

    except UnicodeDecodeError as erruni:
        print(f"An Unicode Error occurred when requesting {url_address},Change byte to string encoding", True)
        res = requests.get(url_address, headers=constants.headers, verify=False)
        is_hacked(content=str(res.content), domain=domain)
    except requests.exceptions.HTTPError as errh:
        print("An Http Error occurred:" + repr(errh), True)
    except requests.exceptions.ConnectionError as errc:  # site is down
        print(str(errc), True)
        if str(errc).__contains__("SSLError"):
            if protocol == 'https':
                print('Trying http')
                is_hacked(url=url, protocol='http', domain=domain)
            elif protocol == 'http':
                print(f"Trying curl for {url}")
                response = utils.curl_request(url)
                return response

            # print("An Error Connecting to the API occurred: " + repr(errc))
        else:
            print("Exist with SSL Issues")
            return False, "ssl_failed"
        # print("An Error Connecting to the API occurred:" + repr(errc))
    except requests.exceptions.Timeout as errt:
        print("A Timeout Error occurred:" + repr(errt), True)
    except requests.exceptions.RequestException as err:
        print(repr(err), True)
    except requests.exceptions.InvalidURL as err:
        print(repr(err), True)


def check_defacement_content_changes(keywords_pattern, current_content, browser_content):
    changes_percentage = 0.0
    if current_content and browser_content:
        changes_percentage = content_changes_percentage(current_content, browser_content)

    keywords_pattern = keywords_pattern.replace("'", "")
    pattern = re.compile(keywords_pattern)
    out = pattern.findall(browser_content.lower())

    if changes_percentage > constants.NOTIFICATION_CHANGES_PERCENTAGE or len(out) > 0:
        return {"is_defaced": True, "status": "defaced", "percentage_changes": float(changes_percentage)}
    return {"is_defaced": False, "status": "safe", "percentage_changes": float(changes_percentage)}


def is_site_active(url, protocol='https'):
    # str_pattern (regex|regex)
    print(f"Checking website status: {protocol}://{url}")
    try:
        r = requests.get(f"{protocol}://{url}", headers=constants.headers, verify=False)
        print(f"Active site {protocol}://{url}")

        if r.status_code == 200:
            print(f"Index page length: {len(r.content)}")
        else:
            if r.status_code == 401:
                print("Require authorization,look like it is on intranet")
            print(f"{r.status_code}:{url}")
        return True, len(r.content)
    except requests.exceptions.HTTPError as errh:
        print(f"An Http Error occurred: " + repr(errh), True)
    except requests.exceptions.ConnectionError as errc:  # site is down
        print(f"Inactive site {protocol}://{url}", True)
        if not str(errc).__contains__("SSLError"):
            if protocol == 'https':
                print("Trying http")
                is_site_active(url, 'http')
            # print("An Error Connecting to the API occurred: " + repr(errc))
        else:
            print("Exist with SSL Issues")
            return True, 0
    except requests.exceptions.Timeout as errt:
        print("A Timeout Error occurred:" + repr(errt), True)
    except requests.exceptions.RequestException as err:
        print(repr(err), True)
    except requests.exceptions.InvalidURL as err:
        print(repr(err), True)
    except Exception as err:
        print(repr(err), True)
    return False, 0


def check_site_status():
    print("Site status check runs every 3 hours")
    sites = db.load_domain_for_status()
    print(f"Len of site status excl sub {len(sites)}")
    # quit()
    for site in sites:
        site_address = site['site_name']
        site_status, index_length = is_site_active(site_address, 'https')

        if site_status:
            db.update_domain_status(site['_id'], {"site_status": "active", "index_page_length": index_length})
        else:
            db.update_domain_status(site['_id'], {"site_status": "inactive", "index_page_length": index_length})


def defacement_checker():
    print("Defacement checking runs every 5 minutes")
    defacement_keywords = db.load_defacement_keywords_names()
    defacement_pattern = defacement_keywords['pattern']
    sites = db.load_domain_to_scan()
    for site in sites:
        site_address = site['site_name']
        protocol = "https"
        site_status = is_hacked(url=site_address, protocol=protocol)

        if site_status['status']:  # send email and set document to defaced
            db.update_domain_status(site['_id'], {"defacement_status": "defaced"})
    return True


def check_site_isp():
    print(f"ISP Checks started at {utils.current_time()}")
    dom_isp = {}
    pattern = re.compile(constants.ASN_PATTERN)
    data = db.load_domain_toscanfor_isp()
    for dom in data:
        if len(dom['site_ip']) > 0:
            dom_isp = where_site_is_hosted(dom['site_ip'][0])
        if dom_isp != {}:
            asn_arr_info = pattern.findall(dom_isp.get('as'))
            if len(asn_arr_info) > 0:
                dom_isp['asn_number'] = asn_arr_info[0]
            print(f"Site {dom['site_name']} hosted by ", dom_isp.get("isp"))
            db.update_domain_status(domain_name=dom['site_name'], obj={"site_isp": dom_isp})
        else:
            print(f"Unable to find ISP for {dom['site_name']}")
        time.sleep(3)
    print(f"ISP Checks ended at {utils.current_time()}")


def update_site_isp():
    print(f"ISP Checks started at {utils.current_time()}")
    data = db.load_unique_ip()
    pattern = re.compile(constants.ASN_PATTERN)
    for dom in data:
        dom_isp = ipinfo_site_data(dom)
        if dom_isp != {}:
            print(f"Site ip {dom} hosted by ", dom_isp.get("isp"))
            dom_isp['asn_number'] = ""
            found_asn_number_arr = pattern.findall(dom_isp.get('as'))
            if len(found_asn_number_arr) > 0:
                dom_isp['asn_number'] = found_asn_number_arr[0]
            db.update_domain_status(site_ip=dom, obj={"site_isp": dom_isp})
        else:
            print(f"Unable to find ISP for {dom}")
        time.sleep(2)
    print(f"ISP Checks ended at {utils.current_time()}")


def update_country_ip_isp():
    print(f"IP ISP Checks started at {utils.current_time()}")
    pattern = re.compile(constants.ASN_PATTERN)
    data = db.load_ip_by_country()
    for dom in data:
        print(dom['_id'])
        dom_isp = ipinfo_site_data(dom['start'])
        if dom_isp != {}:
            print(f"Found {dom['start']}:CURRENT:: {dom['country']} NEW:: {dom_isp['country']}")
            dom_isp['asn_number'] = ""
            found_asn_number_arr = pattern.findall(dom_isp.get('as'))
            if len(found_asn_number_arr) > 0:
                dom_isp['asn_number'] = found_asn_number_arr[0]
            db.update_country_ip_with_isp_info(dom['_id'], dom_isp)
        else:
            print(f"Unable to find ISP for {dom}")
        # quit()

        time.sleep(2)
    print(f"IP ISP Checks ended at {utils.current_time()}")


def where_site_hosted(dom):
    # cookie:
    # 1. visitorFirstLandingPage:	"https://sitechecker.pro/hosting-checker/"
    # 2. qtrans_front_language:	"en"
    # 3. paddlejs_campaign_referrer:	"sitechecker.pro"
    # 4. Response check status
    # Request 0
    # 0. https://sitechecker.pro/wp-admin/admin-ajax.php
    # 1. Body: action=crawler_validate_domain_request&url=http%3A%2F%2F178.238.230.88
    # Request 1
    # 0 https://sitechecker.pro/wp-admin/admin-ajax.php
    # 1. "action":"crawler_get_token"
    # 2. "api":"https://api1.sitechecker.pro"
    # 3. "f4xDur6SBquTACQg":"81799843aa"
    # Response 1
    # 0 {"status":true,"message":{"token":"b7bbbf3f6fa24d629895505862e98cd3343e1b6d920c779bc7e7c1d5b5298e77"}}

    # Request 2
    # 0. https://api1.sitechecker.pro/api/v1/full/38/{token}/http://{ip}
    # Response 2
    # 1.{"data":{"summary":"http:\/\/178.238.230.88","evaluation":100,"group":"","dns":true,"status_code":200,"checks":[{"label":"Website ip checker","title":{"status":"success","country":"Germany","countryCode":"DE","region":"BY","regionName":"Bavaria","city":"Munich","zip":"81549","lat":48.1077,"lon":11.6091,"timezone":"Europe\/Berlin","isp":"Contabo GmbH","org":"Contabo GmbH","as":"AS51167 Contabo GmbH","query":"178.238.230.88"},"group":"IPValidation.Group","subgroup":"IPValidation.Title","importance":"info","description":"Website ip checker","subgroupDescription":"Website ip checker"}]}}
    data = {}
    try:
        print(f"Check where {dom} is hosted")
        url = "https://sitechecker.pro/wp-admin/admin-ajax.php"
        body_validate_url = f"action=crawler_validate_domain_request&url={dom}"
        body_token = "action=crawler_get_token&api=https://api1.sitechecker.pro&f4xDur6SBquTACQg=035d6811b2"
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie': '_a5e87=84de26bef63eb992; qtrans_front_language=en; _wp_visitor=bDJDYkRRRjY4LzRiYjFacW04cVBqUT09; visitorFirstLandingPage=https://sitechecker.pro/hosting-checker/',
                   'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                   'x-requested-with': 'XMLHttpRequest'}
        # Validate URL before accessing it
        res_validate_url = requests.post(url, data=body_validate_url, headers=headers, timeout=90)
        print(res_validate_url.content.decode("utf-8"))
        if res_validate_url.status_code == 200:
            res_validation_data = json.loads(res_validate_url.content.decode("utf-8"))
            if res_validation_data['status']:  # check the site validation status is successful
                # Request token
                res = requests.post(url, data=body_token, headers=headers, timeout=90)
                print(res.status_code, res.headers)
                if res.status_code == 200:
                    token_data = json.loads(res.content.decode("utf-8"))
                    if token_data['status']:
                        # Request ISP Info
                        token = token_data['message']['token']
                        url_isp_check = f"https://api1.sitechecker.pro/api/v1/full/38/{token}/https://{dom}"
                        res_isp_data = requests.get(url_isp_check, headers=constants.headers, timeout=90)
                        print(res_isp_data.content.decode("utf-8"))
                        if res_isp_data.status_code != 200:
                            print(res_isp_data)

                        if res_isp_data.status_code == 200:
                            res_isp = json.loads(res_isp_data.content.decode("utf-8"))
                            # Check if it has verified dns info
                            if res_isp['data']['dns'] and len(res_isp['data']['checks']) > 0:
                                if res_isp['data']['checks'][0]['title']['status'] == "success":
                                    data = res_isp['data']['checks'][0]['title']
                                    print(
                                        f"Domain: {dom} - ISP: {res_isp['data']['checks'][0]['title']['isp']} AS:{res_isp['data']['checks'][0]['title']['as']} ")
                            else:
                                data = res_isp['data']
                                print(
                                    f"ISP Check DNS Verification disabled,Status code:{res_isp['data']['status_code']} DNS:{res_isp['data']['dns']} Checks:{res_isp['data']['checks']}")
            else:
                data = res_validation_data
                print(f"ISP Check {dom} HTTP Status:{res_validation_data['httpStatus']}")
        else:
            print(f"Validation failed {res_validate_url}")

    except Exception as e:
        print(f"Error occurred {repr(e)}", True)
    return data


def where_site_is_hosted(ip):
    data = {}
    try:
        res = requests.get(constants.IPAPI_ISP_LOOKUP_URL.replace('n.n.n.n', ip), verify=True)
        # res = requests.get(f"{constants.IPLOCATION_ISP_LOOKUP_URL}?ip={ip}", verify=True)
        data = res.content.decode('utf-8')
    except Exception as e:
        print(f"ISP Lookup error: {repr(e)}", True)
    return json.loads(data)


def ipinfo_site_data(ip):
    data = {}
    try:
        res = requests.get(constants.IPAPI_ISP_LOOKUP_URL.replace('n.n.n.n', ip), verify=True)
        # res = requests.get(f"{constants.IPINFO_ISP_LOOKUP_URL}{ip}?token={constants.IPINFO_ACCESS_TOKEN}", verify=True)
        data = res.content.decode('utf-8')
        print(f"{res.headers['X-Rl']}:{ip}:{res.status_code}")
    except Exception as e:
        print(f"ISP Lookup error: {repr(e)}", True)
    return json.loads(data)


def check_site_cms(content: str, headers: dict = None):
    res = {"cms_exist": False, "cms_type": "No CMS", "cms_version": "Unknown"}
    wp_pattern = "wp-content/plugins"
    typo3_pattern = "typo3conf/ext"
    typo3_pattern0 = "typo3temp"
    typo3_header_pattern = "X-TYPO3-Parsetime"
    drupal_header_pattern = "x-drupal-cache"
    hubspot_header_pattern = "x-hubspot-correlation-id"
    wix_header_pattern = "x-wix-request-id"
    global_cms_pattern = re.compile('generator\" content=\"[a-zA-Z0-9 .:\/()-]+\"( )?\/>')
    cms_version_match = re.compile("[0-9.]+")
    cms_pattern_matching = global_cms_pattern.search(content.lower())

    if cms_pattern_matching:
        cms_found = cms_pattern_matching.group().split('"')[2]
        cms_version = cms_version_match.search(cms_pattern_matching.group())
        print(cms_found)
        if cms_found.lower().__contains__("wordpress"):
            wp_arr = cms_found.split(" ")
            res = {"cms_exist": True, "cms_type": wp_arr[0], "cms_version": wp_arr[1]}
        elif cms_found.lower().__contains__("drupal"):
            drupal_arr = cms_found.split(" ")
            res = {"cms_exist": True, "cms_type": drupal_arr[0], "cms_version": drupal_arr[1]}
        elif cms_found.lower().__contains__("wix"):
            res = {"cms_exist": True, "cms_type": "Wix", "cms_version": "Unknown"}
        elif cms_found.lower().__contains__("typo3"):
            res = {"cms_exist": True, "cms_type": "Typo3", "cms_version": "Unknown"}
        elif cms_found.lower().__contains__("joomla"):
            res = {"cms_exist": True, "cms_type": "Joomla", "cms_version": "Unknown"}

        else:
            # cms_data: str = cms_pattern_matching.sub("", cms_pattern_matching.group())
            res = {"cms_exist": True, "cms_type": "Unknown", "cms_version": cms_version}

    elif content.__contains__(wp_pattern):
        res = {"cms_exist": True, "cms_type": "Wordpress", "cms_version": "Unknown"}
    elif content.__contains__(typo3_pattern) or content.__contains__(typo3_pattern0):
        res = {"cms_exist": True, "cms_type": "Typo3", "cms_version": "Unknown"}
    elif headers is not None:
        if typo3_header_pattern in headers:
            res = {"cms_exist": True, "cms_type": "Typo3", "cms_version": "Unknown"}
        elif drupal_header_pattern in headers:
            res = {"cms_exist": True, "cms_type": "Drupal", "cms_version": "Unknown"}
        elif hubspot_header_pattern in headers:
            res = {"cms_exist": True, "cms_type": "Hubspot", "cms_version": "Unknown"}
        elif wix_header_pattern in headers:
            res = {"cms_exist": True, "cms_type": "Wix", "cms_version": "Unknown"}

    return res


def server_info(headers: dict):
    res = {"server": None, "x-powered-by": None}
    if "Server" in headers:
        res['server'] = headers.get("Server")
    elif "server" in headers:
        res['server'] = headers.get("server")

    if "X-Powered-By" in headers:
        res['x-powered-by'] = headers.get("X-Powered-By")
    elif "x-powered-by" in headers:
        res['x-powered-by'] = headers.get("x-powered-by")
    return res


def update_expired_domains():
    dom_whois: dict = {}
    print(f"Expired domain update checks started at {utils.current_time()}")
    data = db.load_expired_domain()
    for dom in data:
        print(f"Retrieving whois info of {dom['site_name']}")
        dom_whois = syscmd.run_whois_command(dom['site_name'])
        if dom_whois is None:
            print(f"Quota exceeded at {utils.current_time()}")
            break
        if dom_whois and dom_whois != {}:
            if dom_whois.get('registrant') != {}:
                # print(dom_whois)
                if dom_whois.get("registry").get("expiry_date") != dom.get('registry').get('expiry_date'):
                    dom_whois['whois_recheck_date'] = utils.current_time()
                    db.save_logs(
                        {"action": "Automated Whois update", "message": f"Update whois info of {dom['site_name']}",
                         "cookie": {}, "source_ip": "", "resource": "", "user_agent": "", "auth": ""})
                    print(f"Updating whois info of {dom['site_name']}")
                    db.update_domain_status(domain_name=dom['site_name'],
                                            obj=dom_whois)
                else:
                    print(f"No whois changes update recheck {dom['site_name']}")
                    db.update_domain_status(domain_name=dom['site_name'], obj={"site_status": "domain_unavailable",
                                                                               "whois_recheck_date": utils.current_time()})
            elif dom_whois['registrant'] != {} and dom_whois == {}:
                db.save_logs({"action": "Automated Whois update", "message": f"Update whois info of {dom['site_name']}",
                              "cookie": {}, "source_ip": "", "resource": "", "user_agent": "", "auth": ""})
                print(f"Updating whois info of {dom['site_name']}")
                db.update_domain_status(domain_name=dom['site_name'],
                                        obj=dom_whois)
            else:
                print(f"No whois changes,update recheck {dom['site_name']}")
                db.update_domain_status(domain_name=dom['site_name'], obj={"site_status": "domain_unavailable",
                                                                           "whois_recheck_date": utils.current_time()})
        else:
            print(f"No whois info found,update recheck {dom['site_name']}")
            db.update_domain_status(domain_name=dom['site_name'], obj={"site_status": "domain_unavailable",
                                                                       "whois_recheck_date": utils.current_time()})
        time.sleep(7)
    print(f"Expired domain update checks ended at {utils.current_time()}")


def check_sophos_status():
    print(f"Sophos monitoring started at {utils.current_time()}")
    soph_info = db.load_sophos_info(query={"status": "Up"})
    for soph in soph_info:
        soph_status = syscmd.check_ip_status(soph['ip_address'])
        if type(soph_status) != list:
            if int(soph_status['lost_percentage']) == 100:  # down
                print(f"Updating status of {soph['organization_name']}:Down")
                db.update_sophos_info(soph['_id'], {"disconnection_detection_date": utils.current_time(),
                                                    "status": "Down"})
                db.save_sophos_disconnection(
                    {"organization_id": soph['_id'], "disconnection_detection_date": utils.current_time(),
                     "connection_detection_date": None, "created_at": utils.current_time()})
        else:
            print(f"Skipped {soph['organization_name']}")
        # time.sleep(1)
    print(f"Sophos monitoring ended at {utils.current_time()}")


def recheck_sophos_status():
    print(f"Sophos reverification started at {utils.current_time()}")
    soph_info = db.load_sophos_info(query={"status": "Down"})
    for soph in soph_info:
        soph_status = syscmd.check_ip_status(soph['ip_address'], waiting_time=7)
        print(f"Ping response of {soph['organization_name']}: {soph_status}")
        if type(soph_status) != list and soph_status != {}:
            if int(soph_status['lost_percentage']) <= 50:  # up
                print(f"Updating status of {soph['organization_name']}:Up")
                db.update_sophos_info(soph['_id'],
                                      {"disconnection_detection_date": None, "connection_recheck_date": None,
                                       "status": "Up"})
                db.update_sophos_disconnection(soph['_id'], {"connection_detection_date": utils.current_time()})
            else:
                db.update_sophos_info(soph['_id'],
                                      {"connection_recheck_date": utils.current_time()})
                print(f"No changes {soph['organization_name']}:Down")
        else:
            db.update_sophos_info(soph['_id'],
                                  {"connection_recheck_date": utils.current_time()})
            print(f"Skipped unknown response: {soph['organization_name']} : {soph_status}")
        # time.sleep(1)
    print(f"Sophos reverification ended at {utils.current_time()}")


def sophos_status(ip):
    return syscmd.check_ip_status(ip, waiting_time=7)


def page_changes(url):
    first = utils.load_url(url[0], 'https', timeout=180)
    second = utils.load_url(url[1], 'https', timeout=180)

    percent = content_changes_percentage(first['content'], second['content'])
    # print(f"Changes {percent}%")
    with open("media/first.txt", "w") as f:
        f.write(first['content'])
    with open("media/second.txt", "w") as f:
        f.write(second['content'])


def content_changes_percentage(current_content, browser_content):
    if not browser_content:
        browser_content = ""
    if not current_content:
        current_content = ""

    current_content = current_content[:25000]
    browser_content = browser_content[:25000]
    sm = SequenceMatcher(None, current_content, browser_content)
    changes_percentage = '%.2f' % ((1.0 - sm.ratio()) * 100)

    return abs(float(changes_percentage))


def check_site(domain: str):
    domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_KEEP_WWW_PATTERN, "", domain)
    urls = ["https://" + domain, "http://" + domain]
    for i in range(len(urls)):
        url = urls[i]
        result = {}
        try:
            result = perform_check_site(result, url)
            return result
        except (requests.Timeout, requests.ConnectTimeout, requests.ReadTimeout, TooManyRedirects) as e:
            print(f"error: {e}")
            result["site_status"] = "timeout"
        except requests.exceptions.SSLError as e:
            if i == 1:
                result["site_status"] = "site_down"
            else:
                continue
        except requests.ConnectionError as e:
            print(type(e))
            arg0 = e.args[0]
            print(f"error: {e} | {type(e)} | {type(arg0)}")
            if (isinstance(arg0, MaxRetryError) and
                    (str(arg0.reason.args[0]).__contains__("Name or service not known")
                     or isinstance(arg0.reason, ConnectionError))):
                result["domain_exists"] = False
                result["site_status"] = "domain_unavailable"
            else:
                result["site_status"] = "site_down"
        return result


def perform_check_site(result, url: str):
    # url = "https://" + domain if not domain.startswith("http") else domain
    # failed_socket = False
    # Check if domain exists
    # try:
    #     socket.gethostbyname(domain)
    #     result["domain_exists"] = True
    # except socket.gaierror:
    #     failed_socket = True
    # Check site activity (active or HTTP error)
    result['url'] = url
    response = requests.get(url, timeout=45, allow_redirects=True, verify=False, headers=constants.headers)
    result["status_code"] = response.status_code
    if response.status_code == 200:
        result["site_status"] = "active"
        # Attempt to retrieve server information using BeautifulSoup
        # cms = check_site_cms(str(response.content), response.headers)
        # result = result | cms
        server = server_info(response.headers)
        result['server'] = server

        # ssl = ssl_utils.get_ssl_info(domain)
        # result['ssl_info'] = ssl

        # Get the final redirected URL
        result['current_content'] = str(response.content)
        # result['current_content_hash'] = utils.compute_hash(str(response.content))
        result["index_page"] = response.url if response else ""
        result["index_page_length"] = len(response.content)
    else:
        print(f"SiteCheck::{result['url']}-{response.status_code}")
        result["site_status"] = "site_error"
    return result


if __name__ == '__main__':
    print(sys.argv)
    # status = is_hacked(sys.argv[2], sys.argv[4], current_index_length=0, domain=sys.argv[2])
    # check_site_status()
    # status = is_site_active(sys.argv[2], 'https')
    # defacement_checker()
    # ssl_expiration("cyber.gov.rw")
    # resp = get_ssl_info(sys.argv[1])
    # resp = where_site_hosted(sys.argv[1])
    r = requests.get("https://ibaba.rw", verify=False)
    resp = check_site_cms(r.content.decode("utf-8"), dict(r.headers))
    print(resp)
