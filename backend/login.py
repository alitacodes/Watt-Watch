from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib                  # ✅ correct — werkzeug removed
import jwt
import datetime
import os

app = Flask(__name__)
CORS(app)  # Allow requests from React dev server

# Secret key for JWT — use a strong random string in production
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "watt-watch-secret-change-in-prod")

# ── MD5 helpers ───────────────────────────────────────────────────────────────
# ✅ Added — these were missing, causing NameError crashes
def md5_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

def check_md5_hash(stored_hash: str, password: str) -> bool:
    return stored_hash == md5_hash(password)

# ---------------------------------------------------------------------------
# In-memory user store (replace with a real database in production)
# Passwords are stored as MD5-hashed values using hashlib  ✅ comment fixed
# ---------------------------------------------------------------------------
USERS = {
    "admin": md5_hash("admin123"),        # ✅ was generate_password_hash() — fixed
    "operator": md5_hash("operator123"),  # ✅ was generate_password_hash() — fixed
}


@app.route("/api/login", methods=["POST"])
def login():
    """
    POST /api/login
    Body: { "username": "...", "password": "..." }
    Returns: { "success": true, "token": "...", "user": "..." }
          or { "success": false, "message": "..." }
    """
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "Invalid request body."}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    # Check if user exists
    if username not in USERS:
        return jsonify({"success": False, "message": "Invalid credentials. Access denied."}), 401

    # Verify password
    if not check_md5_hash(USERS[username], password):  # ✅ function now exists — no longer crashes
        return jsonify({"success": False, "message": "Invalid credentials. Access denied."}), 401

    # Generate JWT token (expires in 8 hours)
    token = jwt.encode(
        {
            "user": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({
        "success": True,
        "token": token,
        "user": username,
        "message": "Authentication successful.",
    }), 200


@app.route("/api/verify", methods=["GET"])
def verify():
    """
    GET /api/verify
    Header: Authorization: Bearer <token>
    Verifies a JWT token and returns the user info.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "message": "Missing or invalid token."}), 401

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return jsonify({"success": True, "user": payload["user"]}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid token."}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    """
    POST /api/logout
    Stateless JWT — client should discard the token.
    This endpoint exists as a clean hook for future token blacklisting.
    """
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)