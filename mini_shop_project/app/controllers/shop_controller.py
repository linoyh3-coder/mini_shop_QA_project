from flask import Blueprint, jsonify, request
from app.services.shop_service import ShopService

shop_blueprint = Blueprint('shop', __name__)

@shop_blueprint.route('/products', methods=['GET'])
def get_products():
    try:
        products = ShopService.get_all_products()
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@shop_blueprint.route('/checkout', methods=['POST'])
def checkout():
    """
    🐛 INTENTIONAL BUG 2: The API allows a negative quantity value!
    Sending a negative quantity results in subtracting price (getting paid to take items).
    """
    data = request.get_json()
    cart_items = data.get('cart', [])
    
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
        
    result = ShopService.process_checkout(cart_items)
    return jsonify(result), 200
