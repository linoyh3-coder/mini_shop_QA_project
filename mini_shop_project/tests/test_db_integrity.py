# בדיקות ישירות מול מסד הנתונים (SQL)
import pytest
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../shop.db'))


def test_db_products_not_empty():
    """בדיקת DB: מוודאת שטבלת המוצרים קיימת ומכילה את מוצרי הבסיס"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # שליפת כמות השורות בטבלה
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()

    assert count > 0, "באג ב-DB: טבלת המוצרים ריקה לחלוטין!"