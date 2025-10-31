SERVER_ADDRESS = "http://172.16.32.37:9000"
SERVER_API = f"{SERVER_ADDRESS}/api/v1"
USER_ROLES = ["monitoring", "admin"]
ITERATION_LIMIT = 70
TIMER_SLEEP = 60 * 2  # 2 minute seconds
PAGE_INCREMENT = 10
RW_WEB_PATTERN = '((http(s?)://)?(www.)?[a-z0-9.]+\.rw)'
SUBDOMAIN_PATTERN = '((http(s?)://)?(www.)?[a-z0-9.]+\.[a-z0-9]+\.rw)'
ONLY_DOMAIN_PATTERN = '((http(s?)://)?(www.)?[a-z0-9]+\.rw)'
SPECIAL_DOMAIN_PATTERN = '((http(s?)://)?(www.)?[a-z0-9]+\.(gov|ac|co|org)+\.rw)'
REMOVE_DOMAIN_PREFIX_PATTERN = r'((http(s?)://)?(www.)?)'
REMAIN_WITH_DOMAIN = r'^(?:https?://)?(?:www\.)?([^/]+)'
REMOVE_DOMAIN_PREFIX_KEEP_WWW_PATTERN = r'((http(s?)://)?)'
LINK_PATTERN = "href=[a-z./]+"
EMAIL_PATTERN = "[a-z0-9.]+@[a-z.]+\.[a-z]+"
PHONE_PATTERN = "((25?)[0-9 -]{10,})"
JWT_EXPIRATION_TIME = 60 * 30  # minutes
THREAD_EXECUTOR_REQUEST_LIMIT = 25
REMOTE_URL_REQUEST = "172.16.32.33:9000/api/v1/remote"
COORDINATES_PATTERN = {
    "lat": 'data-lat=\"[0-9.-]+\"',
    "lon": 'data-lon=\"[0-9.-]+\"',
}
COUNTRY_CODE_PATTERN = "flags/iso[a-zA-Z]+\" alt=\"[A-Z]+\""
CITY_PATTERN = "Location: [a-zA-Z0-9 -\/]+( )?<br>"
HOSTING_PROVIDER_PATTERN = "<h5 [a-zA-Z0-9 -\/,.\"]+</h3>"
IPLOCATION_ISP_LOOKUP_URL = "https://api.iplocation.net/"
IPAPI_ISP_LOOKUP_URL = "http://ip-api.com/json/n.n.n.n?fields=24899583"
IPINFO_ISP_LOOKUP_URL = "https://ipinfo.io/"
IPINFO_ACCESS_TOKEN = "bec8d9858729ae"
ASN_PATTERN = "AS[0-9]+"
PING_RESPONSE_PATTERN = "[0-9]+ packets transmitted, [0-9]+ received, [0-9]+% packet loss, time [0-9]+ms"
DATA_PATH = "crawler_api/data"
# headers = {"Cookie":
#                "_tccl_visitor=c90ceeed-dcef-5bf2-b6cf-2478953490a3; _tccl_visit=c90ceeed-dcef-5bf2-b6cf-2478953490a3",
#            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    "Accept-Language": 'en-US,en;q=0.9',
    "Cache-Control": 'max-age=0',
    "Upgrade-Insecure-Requests": '1',
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

CSS_PATTERN = "<link.*>"
SCRIPT_PATTERN = "<script.*></script>"
FORMCSRF_PATTERN = "<input.*type=\"hidden\".*>"
NOTIFICATION_CHANGES_PERCENTAGE = 90
ITEMS_PER_PAGE = 3
not_useful = {"$and": [{"site_name": {"$not": {"$regex": "mail."}}},
                       {"site_name": {"$not": {"$regex": "imap."}}},
                       {"site_name": {"$not": {"$regex": "pop3."}}},
                       {"site_name": {"$not": {"$regex": "ftp"}}},
                       {"site_name": {"$not": {"$regex": "cpcontacts"}}},
                       {"site_name": {"$not": {"$regex": "cpcalendar"}}},
                       {"site_name": {"$not": {"$regex": "cpanel"}}},
                       {"site_name": {"$not": {"$regex": "webdisk"}}},
                       {"site_name": {"$not": {"$regex": "whm"}}},
                       {"site_name": {"$not": {"$regex": "autodiscover"}}},
                       {"site_name": {"$not": {"$regex": "autoconfig"}}},
                       {"site_name": {"$not": {"$regex": "localhost"}}},
                       {"site_name": {"$not": {"$regex": "test"}}},
                       {"site_name": {"$not": {"$regex": "ns1."}}},
                       {"site_name": {"$not": {"$regex": "ns2."}}},
                       {"site_name": {"$not": {"$regex": "old"}}}
                       ]}

CRITICAL_SYS = ['nci.crvs.nida.gov.rw', 'iecms.gov.rw', 'meis.loda.gov.rw', 'landinformation.lands.rw',
                'recruitment.mifotra.gov.rw', 'smartifmis.minecofin.gov.rw', 'umucyo.gov.rw', 'kwivuza.rssb.rw',
                'rra.gov.rw', 'e-learning.rra.gov.rw', 'etax.rra.gov.rw', 'ecms.rra.gov.rw', 'ects.rra.gov.rw',
                'fg.rra.gov.rw', 'selfservice.ippis.rw', 'gov.rw', 'migeprof.gov.rw', 'minisports.gov.rw',
                'minaffet.gov.rw', 'primature.gov.rw', 'minubumwe.gov.rw', 'minagri.gov.rw', 'minecofin.gov.rw',
                'mininfra.gov.rw', 'minaloc.gov.rw', 'myculture.gov.rw', 'mininter.gov.rw', 'moh.gov.rw',
                'mineduc.gov.rw', 'environment.gov.rw', 'minict.gov.rw', 'minijust.gov.rw', 'mifotra.gov.rw',
                'mod.gov.rw', 'minicom.gov.rw', 'cyber.gov.rw', 'space.gov.rw', 'minema.gov.rw', 'cooperation.rw',
                'rssb.rw', 'risa.rw', 'rmi.rw', 'rfl.rw', 'rcb.rw', 'chuk.rw', 'rlma.rw', 'ferwafa.rw', 'ibuka.rw',
                'rdb.rw', 'chub.rw', 'reg.rw', 'wasac.rw', 'rba.co.rw', 'rwandair.com', 'rac.co.rw', 'rnit.rw',
                'rpfinkotanyi.rw', 'paulkagame.com', 'oag.gov.rw', 'nida.gov.rw', 'rtda.gov.rw', 'police.gov.rw',
                'zigamacss.rw', 'rwandamilitaryhospital.rw', 'rura.rw', 'rfi.rw']
