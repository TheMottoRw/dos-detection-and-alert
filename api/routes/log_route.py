import requests
from flask import Blueprint, request
from api.controllers import logs

log_bp = Blueprint("log", __name__, url_prefix="/api/v1")

# Log CRUD
@log_bp.route("/log", methods=["POST"]) 
def create_log():
    return logs.create_log(request.get_json(force=True, silent=False))

@log_bp.route("/log/<id>", methods=["GET"]) 
def get_log(id):
    return logs.get_log(id)

@log_bp.route("/logs", methods=["GET"]) 
def list_logs():
    return logs.list_logs()

@log_bp.route("/log/<id>", methods=["POST"]) 
def update_log(id):
    return logs.update_log(id,request.get_json(force=True, silent=False))

@log_bp.route("/log/<id>/delete", methods=["DELETE"])
def delete_log(id):
    return logs.delete_log(id)
