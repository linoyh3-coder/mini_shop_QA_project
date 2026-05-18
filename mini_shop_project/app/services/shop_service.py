from app.db.database import get_db_connection


class ShopService:

    @staticmethod
    def get_all_products():
        conn = get_db_connection()
        try:
            products = conn.execute("SELECT * FROM products").fetchall()
            return [dict(p) for p in products]
        finally:
            conn.close()

    @staticmethod
    def process_checkout(cart_items):
        """
        Processes purchase of cart items.
        🐛 INTENTIONAL BUG: No stock validation (as per exercise).
        """

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            total_price = 0

            for item in cart_items:
                product_id = item.get('id')
                quantity = item.get('quantity', 1)

                product = cursor.execute(
                    "SELECT * FROM products WHERE id = ?",
                    (product_id,)
                ).fetchone()

                if not product:
                    continue

                product = dict(product)
                total_price += product['price'] * quantity

                # BUG (intentional): no stock validation
                new_stock = product['stock'] - quantity
                cursor.execute(
                    "UPDATE products SET stock = ? WHERE id = ?",
                    (new_stock, product_id)
                )

            conn.commit()
            return {
                "status": "success",
                "total_paid": total_price
            }

        finally:
            conn.close()
