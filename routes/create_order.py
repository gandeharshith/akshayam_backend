from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId
import datetime
# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_LINK")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['app_database']  # Replace 'app_database' with your desired database name
categories_collection = db['categories']
orders_collection = db['orders']

# Blueprint for create order
create_order_bp = Blueprint('create_order', __name__)

@create_order_bp.route('/createorder', methods=['POST'])
def create_order():
    data = request.json
    name = data.get('name')
    mobile_number = data.get('mobile_number')
    address = data.get('address')
    google_maps_location = data.get('google_maps_location', '')
    items = data.get('items', [])  # List of items with quantity and price
    ordered_date = datetime.utcnow()
    if not name or not mobile_number or not address or not items:
        return jsonify({"error": "Name, mobile_number, address, and items are required"}), 400

    total_order_value = 0
    updated_items = []

    # Check stock availability and calculate total value
    for item in items:
        category_name = item.get('category_name')
        item_name = item.get('item_name')
        quantity = item.get('quantity', 0)

        if not category_name or not item_name or quantity <= 0:
            return jsonify({"error": "Each item must have category_name, item_name, and positive quantity"}), 400

        # Find the category and item
        category = categories_collection.find_one({"category_name": category_name})
        if not category:
            return jsonify({"error": f"Category '{category_name}' not found"}), 404

        item_data = next((i for i in category.get('items', []) if i['item_name'] == item_name), None)
        if not item_data:
            return jsonify({"error": f"Item '{item_name}' not found in category '{category_name}'"}), 404

        if item_data['stock_available'] < quantity:
            return jsonify({"error": f"Insufficient stock for item '{item_name}'"}), 400

        # Calculate price for the item and update total
        item_price = item_data['price'] * quantity
        total_order_value += item_price

        # Update stock for this item
        categories_collection.update_one(
            {"category_name": category_name, "items.item_name": item_name},
            {"$inc": {"items.$.stock_available": -quantity}}
        )

        # Add item details to the order
        updated_items.append({
            "category_name": category_name,
            "item_name": item_name,
            "quantity": quantity,
            "price_per_unit": item_data['price'],
            "total_price": item_price
        })

    # Create order with status set to "Order Placed"
    order = {
        "name": name,
        "mobile_number": mobile_number,
        "address": address,
        "google_maps_location": google_maps_location,
        "items": updated_items,
        "total_order_value": total_order_value,
        "status": "Order Placed",
        "ordered_date" : ordered_date
    }

    # Insert the order and get the inserted ID
    inserted_order = orders_collection.insert_one(order)
    order['_id'] = str(inserted_order.inserted_id)  # Convert ObjectId to string

    return jsonify({"message": "Order created successfully", "order": order}), 201
@create_order_bp.route('/update_order_status/<order_id>', methods=['PUT'])
def update_order_status(order_id):
    # Extract the new status from the request body
    data = request.json
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    # Validate the new status (for example, we can allow statuses like "Order Placed", "Processing", "Shipped", "Delivered")
    allowed_statuses = ["Order Placed", "Processing", "Shipped", "Delivered", "Cancelled"]
    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid status"}), 400

    # Find the order by order_id
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Update the status in the database
    orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": new_status}})

    # Return the updated order
    order['status'] = new_status  # Update status in response
    order['_id'] = str(order['_id'])  # Convert ObjectId to string

    return jsonify({"message": "Order status updated successfully", "order": order}), 200
@create_order_bp.route('/get_user_orders/<mobile_number>', methods=['GET'])
def get_user_orders(mobile_number):
    # Find all orders where the mobile_number matches the given parameter
    orders = orders_collection.find({"mobile_number": mobile_number})

    # If no orders are found for the user
    if not orders:
        return jsonify({"error": "No orders found for this user"}), 404

    # Convert ObjectId to string and return the orders
    orders_list = []
    for order in orders:
        order['_id'] = str(order['_id'])  # Convert ObjectId to string
        orders_list.append(order)

    return jsonify({"orders": orders_list}), 200
@create_order_bp.route('/get_all_orders', methods=['GET'])
def get_all_orders():
    # Retrieve all orders and sort them by 'order_date' in descending order (most recent first)
    orders = orders_collection.find().sort("ordered_date", -1)  # -1 for descending order

    # If no orders are found
    if not orders:
        return jsonify({"error": "No orders found"}), 404

    # Convert ObjectId to string and return the orders
    orders_list = []
    for order in orders:
        order['_id'] = str(order['_id'])  # Convert ObjectId to string
        orders_list.append(order)

    return jsonify({"orders": orders_list}), 200
@create_order_bp.route('/delete_order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        # Find the order by its _id (order_id is passed as a URL parameter)
        order = orders_collection.find_one({"_id": ObjectId(order_id)})

        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Delete the order
        orders_collection.delete_one({"_id": ObjectId(order_id)})

        return jsonify({"message": "Order deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500