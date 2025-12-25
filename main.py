from flask import Flask, request, jsonify

app = Flask(__name__)

users = []
user_id_counter = 1

@app.route("/")
def home():
    return {"message": "User Management API is running"}

@app.route("/users", methods=["POST"])
def create_user():
    global user_id_counter

    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Name and email are required"}), 400

    user = {
        "id": user_id_counter,
        "name": data["name"],
        "email": data["email"]
    }

    users.append(user)
    user_id_counter += 1

    return jsonify(user), 201

if __name__ == "__main__":
    app.run(debug=True)
