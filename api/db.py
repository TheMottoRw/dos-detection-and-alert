import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId
import bcrypt

from .config import Config

_client = None
_db = None
_keyword = None
_user = None
_log = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGODB_URI)
    return _client


def get_db():
    global _db
    if _db is None:
        _db = get_client()[Config.DB_NAME]
    return _db


def get_keyword_collection():
    global _keyword
    if _keyword is None:
        _keyword = get_db()["Keywords"]
    return _keyword


def get_user_collection():
    global _user
    if _user is None:
        _user = get_db()["Users"]
    return _user

def get_log_collection():
    global _log
    if _log is None:
        _log = get_db()["Logs"]
    return _log


def ensure_keyword_collection():
    db = get_db()
    keyword = get_keyword_collection()

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "name",
            ],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "objectId"},
                "name": {"bsonType": "string"},
                "createdAt": {"bsonType": "date"},
                "updatedAt": {"bsonType": "date"},
            },
        }
    }

    if "keywords" not in db.list_collection_names():
        db.create_collection(
            "keywords", validator=schema, validationLevel="strict", validationAction="error"
        )
    else:
        db.command(
            {
                "collMod": "keywords",
                "validator": schema,
                "validationLevel": "strict",
                "validationAction": "error",
            }
        )

    # Indexes
    keyword.create_index([("name", ASCENDING)], unique=True, name="uniq_name")


def ensure_user_collection():
    db = get_db()
    users = get_user_collection()

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "email", "password", "userType", "status", "createdAt", "updatedAt"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "objectId"},
                "email": {"bsonType": "string"},
                "name": {"bsonType": "string"},
                "userType": {"bsonType": "string",
                             "enum": ["admin", "user"],
                             },
                "status": {
                    "bsonType": "string",
                    "enum": ["active", "inactive", "blocked", "pending"],
                    "description": "Account status"
                },
                "password": {"bsonType": "binData",
                             },
                "isOtpVerified": {"bsonType": "bool"},
                "otpExpiration": {
                    "bsonType": ["date", "null"],
                    "description": "Expiration time for OTP"
                },
                "createdAt": {"bsonType": "date"},
                "updatedAt": {"bsonType": "date"},
                "isDeleted": {"bsonType": "bool", "description": "Soft delete flag"},
                "deletedAt": {
                    "bsonType": ["date", "null"],
                    "description": "Soft delete timestamp"
                },
                "resetOtpHash": {"bsonType": "string"},
                "resetOtpExpiresAt": {"bsonType": ["date", "null"]},
                "resetOtpAttempts": {"bsonType": ["int", "long" ]},
                "failedLoginAttempts": {"bsonType": ["int", "long"]},
                "lockedUntil": {"bsonType": ["date", "null"]}

            },
        }
    }

    if "Users" not in db.list_collection_names():
        db.create_collection(
            "Users", validator=schema, validationLevel="strict", validationAction="error"
        )
    else:
        db.command(
            {
                "collMod": "Users",
                "validator": schema,
                "validationLevel": "strict",
                "validationAction": "error",
            }
        )

    users.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    users.create_index([("status", ASCENDING)], name="idx_status")
    users.create_index([("isDeleted", ASCENDING)], name="idx_isDeleted")

def ensure_log_collection():
    db = get_db()
    keyword = get_keyword_collection()

    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "ip",
                "action",
                "message",
            ],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "objectId"},
                "ip": {"bsonType": "string"},
                "action": {"bsonType": "string"},
                "message": {"bsonType": "string"},
                "createdAt": {"bsonType": "date"},
                "updatedAt": {"bsonType": "date"},
            },
        }
    }

    if "keywords" not in db.list_collection_names():
        db.create_collection(
            "keywords", validator=schema, validationLevel="strict", validationAction="error"
        )
    else:
        db.command(
            {
                "collMod": "keywords",
                "validator": schema,
                "validationLevel": "strict",
                "validationAction": "error",
            }
        )

    # Indexes
    keyword.create_index([("name", ASCENDING)], unique=True, name="uniq_name")


def ensure_admin():
    db = get_db()
    users = get_user_collection()
    password = os.getenv("ADMIN_PASSWORD", "")  # Default admin password
    print("Password:",password)
    admin = users.find_one({"userType": "admin"})
    if not admin:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({
            "name": "Asua",
            "email": "asua@yopmail.com",
            "userType": "admin",
            "password": hashed,
            "status": "active",
            "isOtpVerified": True,
            "otpExpiration": datetime.now(),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "isDeleted": False,
            "deletedAt": None
        })

