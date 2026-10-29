"""
Digital Notice Board System - Flask Web Application
Provides full REST API and Modern Web Interface.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure package and local imports work properly
try:
    from . import database
except (ImportError, ValueError):
    import database

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize database and sample data
database.init_db()
database.seed_sample_notices()

@app.route("/")
def index():
    return render_template("index.html")

# API Endpoints
@app.route("/api/notices", methods=["GET"])
def api_get_notices():
    sort_by = request.args.get("sort_by", "date_desc")
    category = request.args.get("category", "all")
    search = request.args.get("search", "")
    status = request.args.get("status", "all")
    
    notices = database.get_notices(sort_by=sort_by, category=category, search=search, status=status)
    return jsonify({
        "success": True,
        "count": len(notices),
        "notices": notices
    })

@app.route("/api/notices/<int:notice_id>", methods=["GET"])
def api_get_single_notice(notice_id):
    notice = database.get_notice_by_id(notice_id)
    if not notice:
        return jsonify({"success": False, "error": "Notice not found"}), 404
    return jsonify({"success": True, "notice": notice})

@app.route("/api/notices", methods=["POST"])
def api_create_notice():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    category = (data.get("category") or "General").strip()
    priority = (data.get("priority") or "Normal").strip()
    author = (data.get("author") or "Admin Office").strip()
    is_pinned = 1 if data.get("is_pinned") in [1, "1", True, "true"] else 0
    expires_at = data.get("expires_at")
    
    if not title:
        return jsonify({"success": False, "error": "Title is required"}), 400
    if not content:
        return jsonify({"success": False, "error": "Content is required"}), 400
        
    created = database.create_notice(
        title=title,
        content=content,
        category=category,
        priority=priority,
        author=author or "Admin Office",
        is_pinned=is_pinned,
        expires_at=expires_at or None
    )
    return jsonify({"success": True, "notice": created, "message": "Notice posted successfully"}), 201

@app.route("/api/notices/<int:notice_id>", methods=["PUT"])
def api_update_notice(notice_id):
    data = request.get_json() or {}
    notice = database.get_notice_by_id(notice_id)
    if not notice:
        return jsonify({"success": False, "error": "Notice not found"}), 404
        
    updated = database.update_notice(
        notice_id=notice_id,
        title=data.get("title"),
        content=data.get("content"),
        category=data.get("category"),
        priority=data.get("priority"),
        author=data.get("author"),
        is_pinned=data.get("is_pinned"),
        expires_at=data.get("expires_at"),
        status=data.get("status")
    )
    return jsonify({"success": True, "notice": updated, "message": "Notice updated successfully"})

@app.route("/api/notices/<int:notice_id>", methods=["DELETE"])
def api_delete_notice(notice_id):
    deleted = database.delete_notice(notice_id)
    if not deleted:
        return jsonify({"success": False, "error": "Notice not found or already deleted"}), 404
    return jsonify({"success": True, "message": f"Notice #{notice_id} deleted successfully"})

@app.route("/api/categories", methods=["GET"])
def api_get_categories():
    categories = database.get_categories()
    return jsonify({"success": True, "categories": categories})

@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    stats = database.get_stats()
    return jsonify({"success": True, "stats": stats})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Digital Notice Board running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
