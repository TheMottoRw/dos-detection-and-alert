import os
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from flask import request
import jwt


def to_object_id(value, field="id"):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise ValueError(f"Invalid {field}: {value}")


def get_auth_user_id(as_object_id: bool = True):
    """
    Extract userId from Authorization: Bearer <JWT> header.
    The JWT payload is expected to contain {'user': {'_id': '<string>'}} per login implementation.
    Returns ObjectId by default; if as_object_id=False, returns the string id.
    Raises ValueError on any problem, with a human-readable message.
    """
    auth = request.headers.get("Authorization", "").strip()
    if not auth or not auth.lower().startswith("bearer "):
        raise ValueError("Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1].strip()
    if not token:
        raise ValueError("Missing token")
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY", "your-secret-key"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except Exception:
        raise ValueError("Invalid token")
    user = payload.get("user") or {}
    uid = user.get("_id")
    if not uid:
        raise ValueError("Invalid token payload")
    return to_object_id(uid, field="userId") if as_object_id else uid


def serialize(doc):
    if not doc:
        return None

    def convert(value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        return value

    return convert(doc)
