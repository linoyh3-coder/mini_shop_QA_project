import sqlite3
import os

# הגדרת נתיב דינמי לקובץ ה-DB כדי שיעבוד מכל מקום בפרויקט
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shop.db'))


def get_db_connection():
    """פונקציה לפתיחת חיבור למסד הנתונים"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # מאפשר גישה לנתונים לפי שם העמודה (כמו דיקשנרי)
    return conn


def init_db():
    """אתחול מסד הנתונים - יצירת טבלאות והכנסת נתונים ראשוניים"""
    print("Initializing database...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. יצירת טבלת מוצרים (Products)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # 2. יצירת טבלת הזמנות (Orders) - התיקון קורה כאן כשהחיבור פתוח!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    # 3. הכנסת מוצרים ראשוניים במידה והטבלה ריקה (סידורים לפרויקט)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        initial_products = [
            ('Laptop', 1200.00, 10),
            ('Smartphone', 800.00, 15),
            ('Headphones', 150.00, 30),
            ('Keyboard', 75.00, 5)
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            initial_products
        )
        print("Initial products inserted successfully!")

    # שמירת השינויים וסגירת החיבור בסוף התהליך כולו!
    conn.commit()
    conn.close()
    print("Database initialization complete.")


if __name__ == '__main__':
    init_db()