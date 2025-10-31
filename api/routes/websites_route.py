from flask import Blueprint, request
from api.controllers import website

website_bp = Blueprint("website", __name__, url_prefix="/api/v1")

# Keyword CRUD
@website_bp.route("/website", methods=["POST"]) 
def create_website():
    return website.create_website()

@website_bp.route("/website/<id>", methods=["GET"]) 
def get_website(id):
    return website.get_website(id)

@website_bp.route("/websites", methods=["GET"]) 
def list_websites():
    return website.list_websites()

@website_bp.route("/website/<id>", methods=["POST"]) 
def update_website(id):
    return website.update_website(id,request.get_json(force=True, silent=False))

@website_bp.route("/website/<id>/delete", methods=["POST"])
def delete_website(id):
    return website.delete_website(id)
