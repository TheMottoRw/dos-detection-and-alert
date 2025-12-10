import re
from datetime import datetime
from flask import request, jsonify

from ..db import get_websites_collection
from ..utils import to_object_id, serialize
from api.webmonitor import syscmd, constants
from ..webmonitor.utils import load_url


def create_website():
    data = request.get_json(force=True, silent=False)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    webname = (data.get("name") or "").strip().lower()
    domain = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, '', webname)
    loaded_url = load_url(webname,'https',30)
    # loaded_url.pop("content", None)
    # print(loaded_url)

    ip = syscmd.run_nslookup_command(domain)
    if not domain:
        return jsonify({"error": "name is required"}), 400

    doc = {
        "site_name": domain,
        "site_ip": ip,
        "index_page": loaded_url['redirect_url'],
        "current_page": loaded_url['content'],
        "site_status": loaded_url['status'],
        "created_at": datetime.now(),
    }
    coll = get_websites_collection()
    try:
        res = coll.insert_one(doc)
    except Exception as e:
        # likely duplicate
        return jsonify({"error": str(e)}), 400
    created = coll.find_one({"_id": res.inserted_id})
    return jsonify(serialize(created)), 201


def get_website(id):
    coll = get_websites_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    doc = coll.find_one({"_id": _id})
    if not doc:
        return jsonify({"error": "not found"}), 404
    return jsonify(serialize(doc)), 200


def list_websites():
    coll = get_websites_collection()
    query = {}
    if name := (request.args.get("name") or "").strip().lower():
        query["name"] = name
    docs = [serialize(d) for d in coll.find(query).sort("created_at", -1).limit(200)]
    return jsonify(docs), 200


def update_website(id,payload):
    coll = get_websites_collection()
    try:
        _id = to_object_id(id)
        print(_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    to_set = {}
    if "name" in payload and payload["name"]:
        to_set["site_name"] = str(payload["name"]).strip().lower()
        to_set["index_page"] = ""
    if "status" in payload and payload["status"]:
        to_set["site_status"] = str(payload["status"]).strip().lower()

    if not to_set:
        return jsonify({"error": "No valid fields provided"}), 400

    to_set["updatedAt"] = datetime.now()
    print(to_set)

    res = coll.update_one({"_id": _id}, {"$set": to_set})
    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404

    doc = coll.find_one({"_id": _id})
    return jsonify(serialize(doc)), 200


def delete_website(id):
    coll = get_websites_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    res = coll.delete_one({"_id": _id})
    if res.deleted_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted"}), 200
