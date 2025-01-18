from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId  # For working with ObjectId

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_LINK")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['app_database']  # Replace 'app_database' with your desired database name
categories_collection = db['categories']

# Blueprint for add item
add_item_bp = Blueprint('add_item', __name__)

def convert_objectid(item):
    """
    Convert ObjectId fields in a dictionary to strings for JSON serialization.
    """
    if isinstance(item, ObjectId):
        return str(item)
    elif isinstance(item, dict):
        return {k: convert_objectid(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [convert_objectid(i) for i in item]
    return item

@add_item_bp.route('/additem', methods=['POST'])
def add_item():
    data = request.json
    category_name = data.get('category_name')
    item_name = data.get('item_name')
    description = data.get('description', '')
    quantity = data.get('quantity', 0)
    price = data.get('price', 0.0)
    stock_available = data.get('stock_available', 0)

    if not category_name:
        return jsonify({"error": "Category name is required"}), 400
    if not item_name:
        return jsonify({"error": "Item name is required"}), 400
    if not isinstance(stock_available, int) or stock_available < 0:
        return jsonify({"error": "Stock available must be a non-negative number"}), 400

    # Check if the category exists
    category = categories_collection.find_one({"category_name": category_name})
    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Create a new item with a generated _id (MongoDB ObjectId)
    new_item = {
        "_id": ObjectId(),
        "item_name": item_name,
        "description": description,
        "quantity": quantity,
        "price": price,
        "stock_available": stock_available
    }

    # Update the category to include the new item
    categories_collection.update_one(
        {"category_name": category_name},
        {"$push": {"items": new_item}}
    )

    # Convert ObjectId to string for JSON response
    new_item = convert_objectid(new_item)

    return jsonify({"message": "Item added successfully", "item": new_item}), 201

@add_item_bp.route('/updateitem', methods=['PUT'])
def update_item():
    data = request.json
    category_name = data.get('category_name')
    item_id = data.get('item_id')  # Use the _id of the item (or custom id if you prefer)
    item_name = data.get('item_name')
    description = data.get('description')
    quantity = data.get('quantity')
    price = data.get('price')
    stock_available = data.get('stock_available')

    if not category_name:
        return jsonify({"error": "Category name is required"}), 400
    if not item_id:
        return jsonify({"error": "Item id is required"}), 400

    # Check if the category exists
    category = categories_collection.find_one({"category_name": category_name})
    if not category:
        return jsonify({"error": "Category not found"}), 404

    # Find the item to update in the category's items array
    item = next((item for item in category['items'] if str(item['_id']) == str(item_id)), None)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Prepare fields to update if they are provided
    updated_item = {}
    if item_name is not None:
        updated_item['item_name'] = item_name
    if description is not None:
        updated_item['description'] = description
    if quantity is not None:
        updated_item['quantity'] = quantity
    if price is not None:
        updated_item['price'] = price
    if stock_available is not None:
        updated_item['stock_available'] = stock_available

    # If no fields were provided for updating, return an error
    if not updated_item:
        return jsonify({"error": "No fields to update"}), 400

    # Update the item in the category's items array
    categories_collection.update_one(
        {"category_name": category_name, "items._id": item_id},
        {"$set": {f"items.$.{key}": value for key, value in updated_item.items()}}
    )

    return jsonify({"message": "Item updated successfully"}), 200

@add_item_bp.route('/deleteitem/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        # Find the item in the category
        category = categories_collection.find_one({"items._id": ObjectId(item_id)})

        if not category:
            return jsonify({"error": "Item not found"}), 404

        # Remove the item from the category
        categories_collection.update_one(
            {"category_name": category['category_name']},
            {"$pull": {"items": {"_id": ObjectId(item_id)}}}
        )

        return jsonify({"message": "Item deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@add_item_bp.route('/getitems', methods=['GET'])
def get_all_items_by_category():
    try:
        # Fetch all categories and their items
        categories = categories_collection.find({}, {"_id": 0, "category_name": 1, "items": 1})
        
        # Format the response with items grouped by category
        result = []
        for category in categories:
            category_name = category.get("category_name", "Unknown")
            items = convert_objectid(category.get("items", []))
            result.append({
                "category_name": category_name,
                "items": items
            })

        return jsonify({"categories": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
