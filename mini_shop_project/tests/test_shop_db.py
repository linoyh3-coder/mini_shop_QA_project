import pytest
import sqlite3
import os

# הגדרת נתיב אבסולוטי מדויק לקובץ ה-DB בפרויקט
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shop.db'))


@pytest.fixture
def db_cursor():
    """פיקצ'ר המנהל פתיחה וסגירה אוטומטית של קשר ישיר ל-DB בכל טסט"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    yield cursor
    conn.close()


# ================= PRODUCTS TABLE CHECKS ================= #

def test_db_initial_products_exist(db_cursor):
    """בדיקת שלמות: מוודא שטבלת המוצרים קיימת ומכילה שורות נתונים"""
    db_cursor.execute("SELECT COUNT(*) FROM products")
    count = db_cursor.fetchone()[0]

    assert count > 0, "שגיאת שלמות נתונים: טבלת המוצרים ריקה!"


@pytest.mark.parametrize(
    "product_name, expected_price",
    [
        ["Laptop", 1200.00],
        ["Smartphone", 800.00],
        ["Headphones", 150.00]
    ]
)
def test_db_product_prices_accuracy(db_cursor, product_name, expected_price):
    """בדיקה פרמטרית: מוודא שהמחירים המאוחסנים ב-DB עבור מוצרי הבסיס מדויקים"""
    db_cursor.execute("SELECT price FROM products WHERE name = ?", (product_name,))
    row = db_cursor.fetchone()

    assert row is not None, f"המוצר {product_name} לא נמצא בבסיס הנתונים!"
    assert row[0] == expected_price


# ================= ORDERS TABLE CHECKS ================= #

def test_db_orders_table_structure(db_cursor):
    """בדיקת מבנה: מוודא שטבלת ה-orders החדשה שבנינו קיימת ומגיבה לשאילתות"""
    try:
        db_cursor.execute("SELECT COUNT(*) FROM orders")
        assert True
    except sqlite3.OperationalError:
        pytest.fail("באג במבנה: טבלת orders לא קיימת בבסיס הנתונים!")