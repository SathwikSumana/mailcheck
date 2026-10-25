"""MailCheck Flask API Application.

Provides endpoints for email verification, health checks, and optional static serving.
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from verifier import (
    verify_batch,
    STATUS_LIKELY_DELIVERED,
    STATUS_LIKELY_BOUNCE,
    STATUS_UNKNOWN,
)

# Initialize Flask app
# If static frontend build exists in ../frontend/dist, configure static folder
FRONTEND_DIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)

if os.path.exists(FRONTEND_DIST_DIR):
    app = Flask(__name__, static_folder=FRONTEND_DIST_DIR, static_url_path="")
else:
    app = Flask(__name__)

# Security & CORS configuration
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGIN}})

MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "100"))


@app.route("/api/health", methods=["GET"])
def health_check():
    """Diagnostic health check endpoint for uptime monitoring and deployment verification."""
    return jsonify({
        "status": "healthy",
        "service": "mailcheck-backend",
        "max_batch_size": MAX_BATCH_SIZE,
        "version": "1.0.0",
    }), 200


@app.route("/api/verify", methods=["POST"])
def verify_emails_endpoint():
    """Verify a batch of email addresses.
    
    Expected Request Body:
    {
        "emails": ["user@example.com", "contact@test.org"]
    }
    """
    if not request.is_json:
        return jsonify({
            "error": "Invalid Content-Type. Request body must be valid JSON with 'Content-Type: application/json'."
        }), 400

    try:
        data = request.get_json(silent=False)
    except Exception:
        return jsonify({
            "error": "Malformed JSON payload. Please ensure the request body is valid JSON."
        }), 400

    if data is None or not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object containing an 'emails' key."
        }), 400

    if "emails" not in data:
        return jsonify({
            "error": "Missing required field 'emails'. Please provide an array of email addresses."
        }), 400

    emails = data.get("emails")
    if not isinstance(emails, list):
        return jsonify({
            "error": "The 'emails' field must be a JSON array of strings."
        }), 400

    if len(emails) == 0:
        return jsonify({
            "error": "The 'emails' array cannot be empty. Please submit at least one email address."
        }), 400

    if len(emails) > MAX_BATCH_SIZE:
        return jsonify({
            "error": f"Batch size limit exceeded. Submitted {len(emails)} emails, but maximum allowed per request is {MAX_BATCH_SIZE}."
        }), 400

    try:
        verification_result = verify_batch(emails, max_batch_size=MAX_BATCH_SIZE)
        return jsonify(verification_result), 200
    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 400
    except Exception as exc:
        # Safe error response: do not expose internal stack trace
        app.logger.error("Verification error occurred: %s", exc)
        return jsonify({
            "error": "An internal error occurred while processing the verification request."
        }), 500


# Serve frontend static assets if built for unified single-service deployment
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if os.path.exists(FRONTEND_DIST_DIR):
        file_path = os.path.join(FRONTEND_DIST_DIR, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(FRONTEND_DIST_DIR, path)
        else:
            return send_from_directory(FRONTEND_DIST_DIR, "index.html")
    return jsonify({
        "message": "MailCheck Backend API is active. For API access, use /api/verify or /api/health.",
        "frontend_status": "Frontend not built in this container. Run Vite dev server or build frontend."
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
