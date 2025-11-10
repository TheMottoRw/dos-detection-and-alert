import hashlib
import json
import logging
import re
import ssl
import subprocess
import time
import socket
from datetime import datetime, timezone, timedelta

import csv, os

from dotenv import load_dotenv

from . import constants
# import constants
import requests
import urllib3

from .producer import Producer
# urllib3.disable_warnings()
import threading

load_dotenv()

def is_number(value):
    return isinstance(value, (int, float, complex))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_internet_connected():
    try:
        # Attempt to resolve a well-known DNS server
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error:
        return False


def check_domain_existence(domain_name):
    try:
        socket.setdefaulttimeout(15)
        # Resolve the domain name's IP address
        socket.gethostbyname(domain_name)
        return True
    except socket.gaierror:
        return False


def compute_hash(content):
    # Compute the hash (SHA-256 in this example)
    hash_object = hashlib.sha256(content.encode())
    return hash_object.hexdigest()


def compute_hash_difference(hash1, hash2):
    # Calculate the Hamming distance between the two hashes
    distance = sum(ch1 != ch2 for ch1, ch2 in zip(hash1, hash2))
    # Calculate the percentage difference
    percentage_difference = (distance / len(hash1)) * 100
    return percentage_difference


def current_time():  #
    curr_time = datetime.now().astimezone()
    return curr_time


def get_token_expiration_time():
    now = current_time()
    exp = now + timedelta(hours=5)
    return exp


def get_file_timestamp():
    return str(current_time())[:10].replace(' ', '').replace('-', '').replace(":", '')

def test_csv_file_reading():
    results = []
    path = "/home/soft/python-apps/webcrawler/media/domains"
    os.chdir(path)
    file = "Filtered_domains.csv"
    with open(file, mode='r', encoding="utf-8") as f:
        # reading the CSV file
        csvFile = csv.reader(f)

        # displaying the contents of the CSV file
        for lines in csvFile:
            results.append(lines[0].strip())
    return results


def load_url(url, protocol='https', timeout=45):
    response = {}
    ssl_status = "unknown"
    content = ""
    url_addr = f"{protocol}://{url}"
    try:
        # print(f"Thread ID::{threading.get_ident()} Time::{datetime.now()}")
        res = requests.get(url_addr, timeout=timeout, headers=constants.headers, verify=False)
        # print(f"{res.status_code}:{url_addr} [{len(res.content.decode('utf-8'))}]")
        # content = str(res.content)
        content = res.content.decode(encoding="UTF-8")
        if res.status_code >= 400 or (
                content.__contains__("Index of/") and content.__contains__("cgi-bin")) or content.__contains__(
            "/cgi-sys/defaultwebpage.cgi") or content.lower().__contains__("this account has been suspended"):
            response = {"url": url_addr,"redirect_url": res.url, "content": "site_error", "ssl_status": "active" if res.url.startswith("https:") else "strict_https_and_ssl_failed", "status": "site_error",
                        "status_content": content}
        else:
            response = {"url": url_addr,"redirect_url": res.url, "content": content, "ssl_status": "active" if res.url.startswith("https:") else "strict_https_and_ssl_failed",
                        "headers": res.headers, "status": "active"}
    except UnicodeDecodeError as erruni:
        print(f"An Unicode Error occurred when requesting {url_addr},Change byte to string encoding")
        response = {"url": url_addr, "content": str(content), "ssl_status": "active"}

    except requests.exceptions.HTTPError as errh:
        print(f"An Http Error occurred:" + repr(errh))
        print(f"An Http Error occurred:" + repr(errh))
    except requests.exceptions.SSLError as errh:
        print(f"Error:: {errh}")
        print(f"Trying curl for {url}")
        response = curl_request(url)
    except requests.exceptions.ConnectionError as errc:  # site is down
        print(f"Connection errors::{url_addr}:{str(errc)}")
        print(str(errc))
        if protocol=='https':
            print("Change protocol")
            return load_url(url, protocol="http", timeout=timeout)
        # print("An Error Connecting to the API occurred: " + repr(errc))
        if str(errc).__contains__("ConnectTimeoutError") or str(errc).__contains__("Connection aborted") or str(
                errc).__contains__("RemoteDisconnected") or str(errc).__contains__("ReadTimeoutError"):
            print(f"Site may be down {url} :: {str(errc)}")
            response = {"url": url, "content": "site_down", "ssl_status": ssl_status, "status": "site_down",
                        "status_content": str(errc)}
        elif str(errc).__contains__("NewConnectionError"):
            if protocol == "https":
                response = load_url(url,"http")
            else:
                response = {"url": url, "content": "site_down", "ssl_status": ssl_status,
                            "status": "site_down",
                            "status_content": str(errc)}
        elif str(errc).__contains__("NameResolutionError"):
            response = {"url": url, "content": "domain_unavailable", "ssl_status": ssl_status,
                        "status": "domain_unavailable",
                        "status_content": str(errc)}

        else:
            print(f"Exist with SSL Issues {str(errc)}")
            response = {"url": url, "content": str(errc), "status": "active", "status_content": "",
                        "ssl_status": ssl_status}
        # print("An Error Connecting to the API occurred:" + repr(errc))
    except requests.exceptions.TooManyRedirects as errt:
        response = {"url": url, "content": "Response not available because site has many redirects",
                    "ssl_status": ssl_status, "status": "many_redirects", "status_content": str(errt)}
        print(f"A Site available with many redirects :{url_addr}:: {repr(errt)}", True)
    except requests.exceptions.Timeout as errt:
        print(f"A Timeout Error occurred:{url_addr}::{repr(errt)}", True)
        response = {"url": url, "content": "timeout",
                    "ssl_status": ssl_status, "status": "site_down", "status_content": str(errt)}
    except requests.exceptions.InvalidURL as err:
        print(f"An InvalidURL Error occurred:{url_addr}::{repr(err)}", True)
        response = {"url": url, "content": "invalid_url",
                    "ssl_status": ssl_status, "status": "site_down", "status_content": str(err)}

    except requests.exceptions.RequestException as err:
        print(f"RequestException Error occurred:{url_addr}::{repr(err)}", True)
        print(f"{url_addr} : {response['status']}")
        response = {"url": url, "content": "invalid_url",
                    "ssl_status": ssl_status, "status": "site_down", "status_content": str(err)}
    print(f"{current_time()}:{response['url']}: {response['status']}")
    return response


def get_encoding_type(response_headers: dict):
    # Get the content-type header from the response
    content_type = response_headers.get('content-type')

    # Extract the encoding type from the content-type header
    encoding = None
    if content_type:
        encoding_pos = content_type.find('charset=')
        if encoding_pos != -1:
            encoding = content_type[encoding_pos + len('charset='):]
    return encoding


def curl_request(url):
    response = {}
    ssl_status = "strict_https_and_ssl_failed"
    curl_response = subprocess.run(["curl", "-i", url], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT).stdout.decode('UTF-8')
    location_header_match = re.search(r'Location: (https?://[^\r\n]+)', curl_response)
    location_header = ''
    # If a Location header is found, it contains the final URL after redirection
    if location_header_match:
        location_header= location_header_match.group(1)
    else:
        # If no Location header is found, the original URL was not redirected
        # You can also extract the final URL from the `output` headers
        location_header = url
    if curl_response.upper().__contains__("HTTP/1.1 200 OK"):
        response = {"url": url,"redirect_url": location_header, "content": curl_response, "ssl_status": ssl_status,
                    "status": "active"}
    elif curl_response.__contains__("Could not resolve"):
        response = {"url": url, "content": "domain_unavailable", "ssl_status": ssl_status,
                    "status": "domain_unavailable",
                    "status_content": curl_response}
    elif curl_response.__contains__("Failed to connect"):
        response = {"url": url, "content": "site_down", "ssl_status": ssl_status, "status": "site_down",
                    "status_content": curl_response}
    else:
        response = {"url": url, "content": "strict_https_and_ssl_failed", "ssl_status": ssl_status,
                    "status": "strict_https_and_ssl_failed", "status_content": curl_response}
    return response


if __name__ == '__main__':
    print(get_token_expiration_time())
    # print(test_csv_file_reading())
    # print(take_screenshot("https://zilla.kz","zilla.kz"))
    # print(send_exchange_mail("oma.rw"))
    # print(current_time())
