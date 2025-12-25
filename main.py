from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_connection

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this"
jwt = JWTManager(app)

init_db()

@app.route("/")
def home():
    return {"message": "User Management API is running"}

# REGISTER USER
@app.route("/users", methods=["POST"])
def register_user():
    data = request.get_json()

    if not data or "name" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "Name, email, and password are required"}), 400

    hashed_password = generate_password_hash(data["password"])

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (data["name"], data["email"], hashed_password)
        )

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "id": user_id,
            "name": data["name"],
            "email": data["email"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LOGIN USER
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE email = ?",
        (data["email"],)
    )
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user[1], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user[0]))
    return jsonify({"access_token": access_token}), 200

# PROTECTED ROUTE
@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })

    return jsonify(users), 200

if __name__ == "__main__":
    app.run(debug=True)
