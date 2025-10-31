import os
from typing import Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "monitordos")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "events")

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_collection(name: Optional[str] = None) -> Collection:
    client = get_client()
    db = client[MONGODB_DB]
    coll_name = name or MONGODB_COLLECTION
    return db[coll_name]

def update_domain_status(domain_id=None, obj={}, domain_name=None, site_ip=None):
    res = []
    domain_info = get_collection("domain_info")
    if domain_id:
        domain = domain_info.update({"_id": ObjectId(domain_id)}, {"$set": obj})
    elif domain_name:
        dom = domain_info.find_one({"site_name": domain_name})
        if dom:
            domain = domain_info.update({"site_name": domain_name}, {"$set": obj})
    elif site_ip:
        dom = domain_info.find_one({"site_ip": {"$all": [site_ip]}})
        if dom:
            # if "site_isp" in dom:
            #     obj = dom['site_isp'] | obj['site_isp']
            domain = domain_info.update_many({"site_ip": {"$all": [site_ip]}}, {"$set": obj})
    return True
