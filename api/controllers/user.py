import os
from datetime import datetime, timedelta

from bson import Binary
from flask import Blueprint, request, jsonify
from pymongo.errors import DuplicateKeyError
import bcrypt
import secrets
import jwt

from ..db import get_user_collection
from ..utils import to_object_id, serialize

user_bp = Blueprint("user", __name__, url_prefix="/api/v1")


def _now():
    return datetime.now()


def _public_user(doc: dict):
    if not doc:
        return None
    # Remove sensitive fields
    doc = dict(doc)
    for f in [
        "password",
        "resetOtpHash",
        "resetOtpExpiresAt",
        "resetOtpAttempts",
        "failedLoginAttempts",
        "lockedUntil",
    ]:
        if f in doc:
            doc.pop(f)
    return serialize(doc)


def create_user():
    """
    Create a User document.
    Expected body JSON:
    {
      "email": "user@example.com",
      "password": "plain text password",
      "name": "Optional Name",
      "userType": "user" | "admin" (default: user),
      "status": "active" | "inactive" | "blocked" | "pending" (default: active)
    }
    """
    data = request.get_json(force=True, silent=False)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    name = data.get("name") or ""
    user_type = data.get("userType") or "user"
    status = data.get("status") or "active"

    # bcrypt hash
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    doc = {
        "email": email,
        "name": name,
        "userType": user_type,
        "status": status,
        "password": hashed,
        "isOtpVerified": False,
        "otpExpiration": None,
        "createdAt": _now(),
        "updatedAt": _now(),
        "isDeleted": False,
        "deletedAt": None,
        "failedLoginAttempts": 0,
        "lockedUntil": None,
    }

    users = get_user_collection()
    try:
        res = users.insert_one(doc)
        created = users.find_one({"_id": res.inserted_id})
        return jsonify(_public_user(created)), 201
    except DuplicateKeyError as e:
        msg = "duplicate key"
        if "email" in str(e).lower():
            msg = "email already exists"
        return jsonify({"error": msg}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def get_user(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    doc = users.find_one({"_id": _id, "isDeleted": {"$ne": True}})
    if not doc:
        return jsonify({"error": "not found"}), 404
    return jsonify(_public_user(doc)), 200


def list_users():
    """
    Optional filters:
    - email (exact)
    - status (active/inactive/blocked/pending)
    - userType (admin/user)
    """
    users = get_user_collection()

    query = {}
    if email := request.args.get("email"):
        query["email"] = email.strip().lower()
    if status := request.args.get("status"):
        query["status"] = status
    if user_type := request.args.get("userType"):
        query["userType"] = user_type

    # Exclude soft-deleted users by default
    query["isDeleted"] = {"$ne": True}
    docs = [_public_user(d) for d in users.find(query, {"password": 0}).limit(100)]
    return jsonify(docs), 200


def update_user(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    payload = request.get_json(force=True, silent=False)
    if 'role' in payload:
        payload['userType'] = payload['role']
        payload.pop('role')
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    to_set = {}

    # Updatable fields (must match schema)
    for f in ["email", "name", "status", "userType"]:
        if f in payload:
            if f == "email" and payload[f]:
                to_set[f] = str(payload[f]).strip().lower()
            else:
                to_set[f] = payload[f]

    # password change
    if "password" in payload:
        if not payload["password"]:
            return jsonify({"error": "password cannot be empty"}), 400
        to_set["password"] = bcrypt.hashpw(payload["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    if not to_set:
        return jsonify({"error": "No valid fields provided"}), 400

    to_set["updatedAt"] = _now()

    try:
        res = users.update_one({"_id": _id}, {"$set": to_set})
        if res.matched_count == 0:
            return jsonify({"error": "not found"}), 404
        doc = users.find_one({"_id": _id})
        return jsonify(_public_user(doc)), 200
    except DuplicateKeyError as e:
        msg = "duplicate key"
        if "email" in str(e).lower():
            msg = "email already exists"
        return jsonify({"error": msg}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def update_profile(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    payload = request.get_json(force=True, silent=False)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    to_set = {}

    # Updatable fields (must match schema)
    for f in ["email", "name"]:
        if f in payload:
            if f == "email" and payload[f]:
                to_set[f] = str(payload[f]).strip().lower()
            else:
                to_set[f] = payload[f]

    if not to_set:
        return jsonify({"error": "No valid fields provided"}), 400

    to_set["updatedAt"] = _now()

    try:
        res = users.update_one({"_id": _id}, {"$set": to_set})
        if res.matched_count == 0:
            return jsonify({"error": "not found"}), 404
        doc = users.find_one({"_id": _id})
        # Generate JWT token
        public_user = _public_user(doc)
        token = jwt.encode(
            {
                'user': public_user,
                'exp': datetime.now() + timedelta(days=1)
            },
            os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
            algorithm='HS256'
        )
        return jsonify({"status": 'ok', "token": token}), 200
    except DuplicateKeyError as e:
        msg = "duplicate key"
        if "email" in str(e).lower():
            msg = "email already exists"
        return jsonify({"error": msg}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def delete_user(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    res = users.update_one({"_id": to_object_id(id)}, {"$set": {"isDeleted": True, "deletedAt": _now()}})
    if res.modified_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "deleted"}), 200


# ==== Auth and Account Management ====

def login():
    users = get_user_collection()
    data = request.get_json(force=True, silent=False)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = users.find_one({"email": email, "isDeleted": {"$ne": True}})

    # Generic error to avoid user enumeration
    invalid_msg = {"error": "invalid credentials"}

    if not user:
        return jsonify(invalid_msg), 401
    if user.get("status") == "blocked":
        return jsonify({"error": "account blocked"}), 423

    # Verify password
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), user.get("password", ""))

        print(ok)
    except Exception as e:
        print(e)
        ok = False

    if not ok:
        # increment failed attempts and possibly lock
        # attempts = int(user.get("failedLoginAttempts") or 0) + 1
        # update = {"failedLoginAttempts": attempts}
        # if attempts >= int(os.getenv("LOGIN_MAX_ATTEMPTS", "5")):
        #     lock_minutes = int(os.getenv("LOGIN_LOCK_MINUTES", "15"))
        #     update["lockedUntil"] = _now() + timedelta(minutes=lock_minutes)
        # users.update_one({"_id": user["_id"]}, {"$set": update})
        return jsonify(invalid_msg), 401

    # success: reset counters
    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"failedLoginAttempts": 0, "lockedUntil": None, "updatedAt": _now()}},
    )

    # Generate JWT token
    public_user = _public_user(users.find_one({"_id": user["_id"]}))
    token = jwt.encode(
        {
            'user': public_user,
            'exp': datetime.now() + timedelta(days=1)
        },
        os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
        algorithm='HS256'
    )

    return jsonify({"status": "ok", "token": token}), 200


def _send_email_stub(to_email: str, subject: str, body: str, otp_debug: str | None = None):
    # Minimal stub: log to stdout. In production, integrate an email provider.
    print(f"[EMAIL] to={to_email} subject={subject} body={body}")
    if os.getenv("DEBUG_OTP_IN_RESPONSE", "false").lower() == "true" and otp_debug:
        return otp_debug
    return None


def request_password_reset():
    users = get_user_collection()
    data = request.get_json(force=True, silent=False)
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "email is required"}), 400

    user = users.find_one({"email": email, "isDeleted": {"$ne": True}})
    # Always return success to avoid enumeration, but only proceed if user exists
    if user:
        # Generate OTP and store hash + expiry
        otp = f"{secrets.randbelow(1000000):06d}"
        otp_hash = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        expires_minutes = int(os.getenv("RESET_OTP_EXPIRES_MINUTES", "10"))
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "resetOtpHash": otp_hash,
                "resetOtpExpiresAt": _now() + timedelta(minutes=expires_minutes),
                "resetOtpAttempts": 0,
                "updatedAt": _now(),
            }}
        )
        maybe_otp = _send_email_stub(
            email,
            "Your password reset OTP",
            f"Your OTP is {otp}. It expires in {expires_minutes} minutes.",
            otp_debug=otp,
        )
        if maybe_otp:
            # For debugging environments only; controlled by env var
            return jsonify({"status": "ok", "debugOtp": maybe_otp}), 200

    return jsonify({"status": "ok"}), 200


def reset_password():
    users = get_user_collection()
    data = request.get_json(force=True, silent=False)
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()
    new_password = data.get("new_password") or ""

    if not email or not otp or not new_password:
        return jsonify({"error": "email, otp, and new_password are required"}), 400

    user = users.find_one({"email": email, "isDeleted": {"$ne": True}})
    if not user:
        # Hide enumeration
        return jsonify({"error": "invalid otp or expired"}), 400

    # Validate expiry
    expires_at = user.get("resetOtpExpiresAt")
    if not expires_at or expires_at <= _now():
        return jsonify({"error": "invalid otp or expired"}), 400

    # Validate attempts
    attempts = int(user.get("resetOtpAttempts") or 0)
    max_attempts = int(os.getenv("RESET_OTP_MAX_ATTEMPTS", "5"))
    if attempts >= max_attempts:
        return jsonify({"error": "otp attempts exceeded"}), 429

    # Check OTP
    otp_hash = user.get("resetOtpHash") or ""
    valid = False
    try:
        valid = bcrypt.checkpw(otp.encode("utf-8"), otp_hash.encode("utf-8"))
    except Exception:
        valid = False

    if not valid:
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"resetOtpAttempts": attempts + 1, "updatedAt": _now()}},
        )
        return jsonify({"error": "invalid otp or expired"}), 400

    # Set new password and clear OTP fields
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": new_hash, "updatedAt": _now()},
         "$unset": {"resetOtpHash": "", "resetOtpExpiresAt": "", "resetOtpAttempts": ""}}
    )

    return jsonify({"status": "password updated"}), 200
def reset_user_password(id):
    users = get_user_collection()
    data = request.get_json(force=True, silent=False)
    email = (data.get("email") or "").strip().lower()
    new_password = data.get("password") or ""
    try:
        _id = to_object_id(id)
        user = users.find_one({"_id": _id, "isDeleted": {"$ne": True}})
        if not user:
            return jsonify({"error": "user does not exist"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not new_password:
        return jsonify({"error": "Password is required"}), 400

    # Set new password and clear OTP fields
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": new_hash, "updatedAt": _now()},
         "$unset": {"resetOtpHash": "", "resetOtpExpiresAt": "", "resetOtpAttempts": ""}}
    )
    return jsonify({"status": "password updated"}), 200


def change_password(id):
    users = get_user_collection()
    data = request.get_json(force=True, silent=False)
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "current password, new password and confirm password are required"}), 400

    user = users.find_one({"_id": to_object_id(id), "isDeleted": {"$ne": True}})
    if not user:
        # Hide enumeration
        return jsonify({"error": "user does not exist"}), 400

    valid = False
    try:
        valid = bcrypt.checkpw(current_password.encode("utf-8"), user.get("password", ""))

        if valid:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            print({"_id": to_object_id(id)})
            c = users.update_one({"_id": to_object_id(id)}, {"$set": {"password": hashed}})
            if c.matched_count == 0:
                return jsonify({"error": "Failed to update password"}), 400
            return jsonify({"message": "Password updated"}), 200
        else:
            return jsonify({"error": "Invalid current password"}), 400
    except Exception as e:
        valid = False

        return jsonify({"error": "invalid password " + str(e)}), 400

    return jsonify({"message": "password updated"}), 200


def lock_user(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    body = request.get_json(silent=True) or {}
    minutes = int(body.get("minutes") or 0)
    lock_until = None
    if minutes > 0:
        lock_until = _now() + timedelta(minutes=minutes)

    res = users.update_one(
        {"_id": _id},
        {"$set": {"status": "deactive", "lockedUntil": lock_until, "updatedAt": _now()}}
    )
    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "locked", "lockedUntil": lock_until.isoformat() if lock_until else None}), 200


def unlock_user(id):
    users = get_user_collection()
    try:
        _id = to_object_id(id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    res = users.update_one(
        {"_id": _id},
        {"$set": {"status": "active", "failedLoginAttempts": 0, "lockedUntil": None, "updatedAt": _now()}}
    )
    if res.matched_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "unlocked"}), 200

