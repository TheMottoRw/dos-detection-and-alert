from flask import Blueprint
from api.controllers import user

user_bp = Blueprint("user", __name__, url_prefix="/api/v1")

# User CRUD
@user_bp.route("/user", methods=["POST"])
def create_user():
    return user.create_user()

@user_bp.route("/user/<id>", methods=["GET"])
def get_user(id):
    return user.get_user(id)

@user_bp.route("/users", methods=["GET"])
def list_users():
    return user.list_users()

@user_bp.route("/user/<id>", methods=["POST"])
def update_user(id):
    return user.update_user(id)

@user_bp.route("/user/<id>/profile", methods=["POST"])
def update_profile(id):
    return user.update_profile(id)

@user_bp.route("/user/<id>/delete", methods=["DELETE"])
def delete_user(id):
    return user.delete_user(id)

# Auth and account management
@user_bp.route("/auth/login", methods=["POST"])
def login():
    return user.login()

@user_bp.route("/auth/request-password-reset", methods=["POST"])
def request_password_reset():
    return user.request_password_reset()

@user_bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    return user.reset_password()

@user_bp.route("/user/<id>/change-password", methods=["POST"])
def change_password(id):
    return user.change_password(id)

@user_bp.route("/user/<id>/lock", methods=["POST"])
def lock_user(id):
    return user.lock_user(id)

@user_bp.route("/user/<id>/unlock", methods=["POST"])
def unlock_user(id):
    return user.unlock_user(id)
