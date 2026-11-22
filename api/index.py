import os
import sys
import json
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, session

# Add workspace root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from src.rag.pipeline import get_rag_pipeline
from src.vectorstore.chroma_store import get_vector_store
from src.database.mysql_db import get_db_manager
from src.auth.auth_service import get_auth_service
from src.models.intent_classifier import get_intent_classifier
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Flask application
app = Flask(__name__, static_folder="../public", static_url_path="")
app.secret_key = settings.SECRET_KEY

# Ensure vector store has data
def ensure_initialized():
    try:
        vstore = get_vector_store()
        if vstore.count() == 0:
            logger.info("ChromaDB is empty on startup. Triggering sample ingestion...")
            from src.ingestion.ingest import IngestionPipeline
            ingestor = IngestionPipeline()
            docs, chunks = ingestor.process_sample_data()
            if chunks:
                vstore.add_chunks(chunks)
        
        # Ensure demo users exist in MySQL
        auth = get_auth_service()
        auth.create_demo_users_if_not_exist()
    except Exception as e:
        logger.error(f"Initialization check warning: {e}")

ensure_initialized()

# CORS configuration
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

# Serve Frontend
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# ================= API ENDPOINTS =================

@app.route("/api/status", methods=["GET"])
def get_system_status():
    """Returns database connection status and model statistics."""
    db = get_db_manager()
    vstore = get_vector_store()
    classifier = get_intent_classifier()
    
    db_stats = db.get_stats()
    v_stats = vstore.get_stats()
    
    return jsonify({
        "status": "online",
        "project": settings.PROJECT_NAME,
        "database": {
            "engine": db_stats["engine"],
            "host": db_stats["host"],
            "database": db_stats["database"],
            "is_mysql": db_stats["is_mysql"],
            "total_users": db_stats["total_users"],
            "total_queries": db_stats["total_queries"]
        },
        "knowledge_base": {
            "chunks": v_stats["total_chunks"],
            "status": v_stats["status"]
        },
        "model": {
            "name": classifier.metadata.get("model_name", "AWSSupportIntentClassifier-v2"),
            "latency": classifier.metadata.get("avg_inference_latency_ms", 1.0)
        }
    })

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    role = data.get("role", "user")
    
    auth = get_auth_service()
    success, msg, user = auth.register_user(username=username, email=email, password=password, role=role)
    
    if not success:
        return jsonify({"success": False, "message": msg}), 400
    
    clean_user = {"id": user["id"], "username": user["username"], "email": user["email"], "role": user["role"]}
    return jsonify({"success": True, "message": msg, "user": clean_user})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    identifier = data.get("identifier", "")
    password = data.get("password", "")
    
    auth = get_auth_service()
    client_ip = request.remote_addr or "127.0.0.1"
    success, msg, user = auth.login_user(username_or_email=identifier, password=password, ip_address=client_ip)
    
    if not success:
        return jsonify({"success": False, "message": msg}), 401
    
    clean_user = {"id": user["id"], "username": user["username"], "email": user["email"], "role": user["role"]}
    session["user"] = clean_user
    return jsonify({"success": True, "message": msg, "user": clean_user})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    user_id = data.get("user_id")
    top_k = data.get("top_k", settings.TOP_K)
    similarity_threshold = data.get("similarity_threshold", settings.SIMILARITY_THRESHOLD)
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    
    pipeline = get_rag_pipeline()
    pipeline.retriever.top_k = int(top_k)
    pipeline.retriever.similarity_threshold = float(similarity_threshold)
    
    response = pipeline.get_rag_response(
        query=query,
        user_id=int(user_id) if user_id else None
    )
    
    return jsonify({
        "query": response["query"],
        "answer": response["answer"],
        "sources": response["sources"],
        "classification": response["classification"],
        "metadata": response["metadata"]
    })

@app.route("/api/chat/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"history": []})
    
    db = get_db_manager()
    records = db.get_chat_history(user_id=int(user_id), limit=50)
    return jsonify({"history": records})

@app.route("/api/chat/history", methods=["DELETE"])
def clear_history():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    db = get_db_manager()
    db.clear_chat_history(user_id=int(user_id))
    return jsonify({"success": True, "message": "History cleared successfully."})

@app.route("/api/admin/audit-logs", methods=["GET"])
def get_audit_logs():
    db = get_db_manager()
    logs = db.get_audit_logs(limit=25)
    return jsonify({"logs": logs})

# Local server runner
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n" + "=" * 65)
    print(f"  AWS Technical Support Assistant Server Ready!")
    print(f"  Open in your browser: http://localhost:{port}")
    print("=" * 65 + "\n")
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=port, _quiet=True)
    except Exception:
        app.run(host="0.0.0.0", port=port, debug=False)
