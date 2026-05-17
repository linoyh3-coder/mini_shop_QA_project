import os
import sqlite3
import pytest
import requests

# Define local base configurations for the running web application
BASE_URL = "http://127.0.0.1:5000/api"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shop.db'))

def get_actual_stock(product_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    product = cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product['stock'] if product else None

def test_get_products_api():
    """
    Sanity Verification: Checks if the products catalog endpoint returns HTTP 200 and explicit products data.
    """
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 200, f"Expected 200 OK but received {response.status_code}"
    products = response.json()
    assert len(products) > 0, "Products array should not be empty"
    assert "name" in products[0], "Product entry must feature a 'name' attribute"

def test_negative_quantity_checkout_bug():
    """
    Security / Validation Test: Verifies if the backend filters out exploit inputs like a negative quantity.
    🐛 This test acts to catch INTENTIONAL BUG 2 (negative quantity allows a zero/reverse bill balance).
    """
    payload = {
        "cart": [
            {"id": 1, "quantity": -3}
        ]
    }
    response = requests.post(f"{BASE_URL}/checkout", json=payload)
    
    # In a fully secure architecture, this request must be rejected (HTTP 400 Bad Request)
    # The current vulnerable backend handles it as valid (HTTP 200) and computes a negative sum.
    print(f"\n[Negative Quantity Test Result Update] Status code: {response.status_code}, Response Body: {response.json()}")
    
    # Asserting that the backend should reject negative quantity (Expected standard Behavior)
    # This assertion is designed to fail initially on your raw app to prove the test works!
    assert response.status_code == 400, "Security Warning: Backend approved a negative quantity payload!"

def test_negative_stock_limit_bug():
    """
    Integrity Boundary Test: Checks if users can purchase more units than what's available inside store inventories.
    🐛 This test acts to catch INTENTIONAL BUG 1 (lack of validation logic creates negative values in DB).
    """
    initial_stock = get_actual_stock(1)
    print(f"\nInitial database stock balance for Product 1: {initial_stock}")
    
    # Order an amount higher than available inventory capacity
    over_order_quantity = initial_stock + 10
    payload = {
        "cart": [
            {"id": 1, "quantity": over_order_quantity}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/checkout", json=payload)
    assert response.status_code == 200 or response.status_code == 400
    
    updated_stock = get_actual_stock(1)
    print(f"Updated database stock balance for Product 1 after purchase payload: {updated_stock}")
    
    # This assertion catches the error: If stock dropped below zero, the product inventory logic is broken
    assert updated_stock >= 0, f"Critical Bug Detected: Database inventory dipped below zero! Stock balance: {updated_stock}"
