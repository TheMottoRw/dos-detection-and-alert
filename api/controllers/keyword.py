from datetime import datetime
from flask import request, jsonify

from ..db import get_keyword_collection
from ..utils import to_object_id, serialize


def create_keyword():
    data = request.get_json(force=True, silent=False)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    name = (data.get("name") or "").strip().lower()
    if not name:
        return jsonify({"error": "name is required"}), 400

    doc = {
        "name": name,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
    }
    coll = get_keyword_collection()
    try:
        res = coll.insert_one(doc)
    except Exception as e:
        # likely duplicate
        return jsonify({"error": str(e)}), 400
    created = coll.find_one({"_id": res.inserted_id})
    return jsonify(serialize(created)), 201


def get_keyword(id):
    coll = get_keyword_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    doc = coll.find_one({"_id": _id})
    if not doc:
        return jsonify({"error": "not found"}), 404
    return jsonify(serialize(doc)), 200


def list_keywords():
    coll = get_keyword_collection()
    query = {}
    if name := (request.args.get("name") or "").strip().lower():
        query["name"] = name
    docs = [serialize(d) for d in coll.find(query).sort("createdAt", -1).limit(200)]
    return jsonify(docs), 200


def update_keyword(id,payload):
    coll = get_keyword_collection()
    try:
        _id = to_object_id(id)
        print(_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    to_set = {}
    if "name" in payload and payload["name"]:
        to_set["name"] = str(payload["name"]).strip().lower()

    if not to_set:
        return jsonify({"error": "No valid fields provided"}), 400

    to_set["updatedAt"] = datetime.now()
    print(to_set)

    res = coll.update_one({"_id": _id}, {"$set": to_set})
    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404

    doc = coll.find_one({"_id": _id})
    return jsonify(serialize(doc)), 200


def delete_keyword(id):
    coll = get_keyword_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    res = coll.delete_one({"_id": _id})
    if res.deleted_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted"}), 200
