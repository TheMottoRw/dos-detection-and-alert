from datetime import datetime
from flask import request, jsonify

from ..db import get_log_collection
from ..utils import to_object_id, serialize


def create_log(data):
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    ip = (data.get("ip") or "").strip()
    action = (data.get("action") or "").strip()
    message = (data.get("message") or "").strip()

    if not ip or not action or not message:
        return jsonify({"error": "ip, action and message are required"}), 400

    doc = {
        "ip": ip,
        "action": action,
        "message": message,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
    }
    coll = get_log_collection()
    res = coll.insert_one(doc)
    created = coll.find_one({"_id": res.inserted_id})
    return jsonify(serialize(created)), 201


def get_log(id):
    coll = get_log_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    doc = coll.find_one({"_id": _id})
    if not doc:
        return jsonify({"error": "not found"}), 404
    return jsonify(serialize(doc)), 200


essential_log_filters = {"ip", "action"}


def list_logs():
    coll = get_log_collection()
    query = {}
    for k in essential_log_filters:
        v = (request.args.get(k) or "").strip()
        if v:
            query[k] = v
    docs = [serialize(d) for d in coll.find(query).sort("createdAt", -1).limit(200)]
    return jsonify(docs), 200


def update_log(id,payload):
    coll = get_log_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    to_set = {}
    for f in ["ip", "action", "message"]:
        if f in payload:
            to_set[f] = payload[f]

    if not to_set:
        return jsonify({"error": "No valid fields provided"}), 400

    to_set["updatedAt"] = datetime.now()

    res = coll.update_one({"_id": _id}, {"$set": to_set})
    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404

    doc = coll.find_one({"_id": _id})
    return jsonify(serialize(doc)), 200


def delete_log(id):
    coll = get_log_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    res = coll.delete_one({"_id": _id})
    if res.deleted_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted"}), 200
