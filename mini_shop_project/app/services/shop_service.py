from app.db.database import get_db_connection

class ShopService:
    
    @staticmethod
    def get_all_products():
        conn = get_db_connection()
        products = conn.execute("SELECT * FROM products").fetchall()
        conn.close()
        return [dict(p) for p in products]

    @staticmethod
    def process_checkout(cart_items):
        """
        Processes purchase of cart items.
        🐛 INTENTIONAL BUG 1: No verification if the requested quantity exceeds the actual stock,
        which allows negative stock quantities in the DB!
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total_price = 0
        for item in cart_items:
            product_id = item.get('id')
            quantity = item.get('quantity', 1)
            
            product = cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if not product:
                continue
                
            product = dict(product)
            total_price += product['price'] * quantity
            
            # The Bug: Deducting stock directly without boundary control
            new_stock = product['stock'] - quantity
            cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        
        conn.commit()
        conn.close()
        return {"status": "success", "total_paid": total_price}
