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

# Blueprint for signup
signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    mobile_number=data.get('mobile_number')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    users_collection.insert_one({"email": email, "password": password,"mobile_number": mobile_number})
    return jsonify({"message": "Signup successful"}), 201
