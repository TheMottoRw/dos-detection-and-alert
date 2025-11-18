from flask import Blueprint
from api.controllers import dashboard

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1")


@dashboard_bp.route("/dashboard", methods=["GET"]) 
def get_dashboard():
    return dashboard.get_dashboard_stats()
