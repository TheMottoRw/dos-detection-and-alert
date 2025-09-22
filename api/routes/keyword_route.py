from flask import Blueprint, request
from api.controllers import keyword

keyword_bp = Blueprint("keyword", __name__, url_prefix="/api/v1")

# Keyword CRUD
@keyword_bp.route("/keyword", methods=["POST"]) 
def create_keyword():
    return keyword.create_keyword()

@keyword_bp.route("/keyword/<id>", methods=["GET"]) 
def get_keyword(id):
    return keyword.get_keyword(id)

@keyword_bp.route("/keywords", methods=["GET"]) 
def list_keywords():
    return keyword.list_keywords()

@keyword_bp.route("/keyword/<id>", methods=["POST"]) 
def update_keyword(id):
    return keyword.update_keyword(id,request.get_json(force=True, silent=False))

@keyword_bp.route("/keyword/<id>/delete", methods=["POST"])
def delete_keyword(id):
    return keyword.delete_keyword(id)
