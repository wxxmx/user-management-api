from flask import Flask, request, jsonify
from database import init_db, get_connection

app = Flask(__name__)

init_db()

@app.route("/")
def home():
    return {"message": "User Management API is running"}

# CREATE user (POST /users)
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Name and email are required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (data["name"], data["email"])
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

# GET all users (GET /users)
@app.route("/users", methods=["GET"])
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
