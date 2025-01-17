from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_LINK")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['app_database']  # Replace 'app_database' with your desired database name
categories_collection = db['categories']

# Blueprint for add category
add_category_bp = Blueprint('add_category', __name__)

@add_category_bp.route('/addcategory', methods=['POST'])
def add_category():
    data = request.json
    category_name = data.get('category_name')
    description = data.get('description', '')

    if not category_name:
        return jsonify({"error": "Category name is required"}), 400

    # Check if the category already exists
    if categories_collection.find_one({"category_name": category_name}):
        return jsonify({"error": "Category already exists"}), 400

    # Insert the category into the database
    new_category = {
        "category_name": category_name,
        "description": description
    }
    categories_collection.insert_one(new_category)

    return jsonify({"message": "Category added successfully"}), 201
