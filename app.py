import os
from datetime import datetime

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from api import db
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()

app = Flask(__name__)

# Register API blueprints
try:
    from api.routes.user_route import user_bp as user_routes
    app.register_blueprint(user_routes)
except Exception as e:
    # Fallback: continue running core endpoints even if user routes fail to import
    print(f"[WARN] Failed to register user routes: {e}")

try:
    from api.routes.log_route import log_bp as log_routes
    app.register_blueprint(log_routes)
except Exception as e:
    print(f"[WARN] Failed to register log routes: {e}")

try:
    from api.routes.keyword_route import keyword_bp as keyword_routes
    app.register_blueprint(keyword_routes)
except Exception as e:
    print(f"[WARN] Failed to register keyword routes: {e}")

# ---- Swagger (OpenAPI) setup ----
try:
    from flasgger import Swagger

    def build_paths_from_app(flask_app: Flask):
        paths = {}
        for rule in flask_app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue
            path = rule.rule
            # Convert Flask variable syntax <var> or <type:var> to OpenAPI {var}
            # e.g., /user/<id> -> /user/{id}
            segs = []
            for part in path.split('/'):
                if part.startswith('<') and part.endswith('>'):
                    name = part[1:-1]
                    if ':' in name:
                        name = name.split(':', 1)[1]
                    segs.append('{' + name + '}')
                else:
                    segs.append(part)
            oapi_path = '/'.join(segs)
            if not oapi_path.startswith('/'):
                oapi_path = '/' + oapi_path

            methods = (rule.methods or set()) - {'HEAD', 'OPTIONS'}
            ops = {}
            for m in sorted(methods):
                ops[m.lower()] = {
                    "summary": f"{m} {oapi_path}",
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            if ops:
                paths.setdefault(oapi_path, {}).update(ops)
        return paths

    template = {
        "openapi": "3.0.3",
        "info": {
            "title": "MonitorDOS API",
            "description": "Auto-generated documentation of all registered routes.",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "/"}
        ],
        "paths": build_paths_from_app(app)
    }

    swagger = Swagger(app, template=template, config={
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,  # include all endpoints
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/swagger"
    })
except Exception as e:
    print(f"[WARN] Swagger UI not initialized: {e}")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat() + "Z"})


@app.post("/events")
def create_event():
    data = request.get_json(silent=True) or {}
    # Attach server timestamp if not provided
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat() + "Z"
    try:
        coll = get_collection()
        result = coll.insert_one(data)
        return jsonify({"inserted_id": str(result.inserted_id)}), 201
    except ServerSelectionTimeoutError:
        return jsonify({"error": "database_unavailable"}), 503


@app.get("/events")
def list_events():
    try:
        coll = get_collection()
        docs = []
        for doc in coll.find().sort("timestamp", -1).limit(50):
            doc["_id"] = str(doc["_id"])  # make JSON serializable
            docs.append(doc)
        return jsonify(docs)
    except ServerSelectionTimeoutError:
        return jsonify({"error": "database_unavailable"}), 503


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found on this server",
        "status": 404
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Internal glitch",
        "message": "Something went wrong on our end. Please try again later.",
        "status": 500
    }), 500

@app.errorhandler(405)
def server_error(error):
    return jsonify({
        "error": "Method not allowed",
        "status": 405
    }), 405


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    db.ensure_user_collection()
    db.ensure_admin()
    db.ensure_keyword_collection()
    db.ensure_log_collection()


    app.run(host=host, port=port, debug=debug)
