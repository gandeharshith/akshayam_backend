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

# Blueprint for delete category
delete_category_bp = Blueprint('delete_category', __name__)

@delete_category_bp.route('/deletecategory', methods=['DELETE'])
def delete_category():
    data = request.json
    category_name = data.get('category_name')

    if not category_name:
        return jsonify({"error": "Category name is required"}), 400

    # Check if the category exists
    category = categories_collection.find_one({"category_name": category_name})
    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Delete the category
    categories_collection.delete_one({"category_name": category_name})

    return jsonify({"message": "Category deleted successfully"}), 200
