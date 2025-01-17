from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_LINK")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['user_database']
users_collection = db['users']

# Blueprint for forgot password
forgot_password_bp = Blueprint('forgot_password', __name__)

@forgot_password_bp.route('/forgotpassword', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    users_collection.update_one({"email": email}, {"$set": {"password": new_password}})
    return jsonify({"message": "Password updated successfully"}), 200
