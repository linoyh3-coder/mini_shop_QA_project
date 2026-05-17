import pytest
from app.db.database import get_db_connection, init_db


# ================= FIXTURES ================= #

@pytest.fixture(autouse=True)
def init_database():
    """
    אתחול DB לפני כל בדיקה
    """
    init_db()


@pytest.fixture
def db_connection():
    """
    חיבור זמני למסד הנתונים
    """
    conn = get_db_connection()
    yield conn
    conn.close()


# ================= PRODUCTS TABLE TESTS ================= #

@pytest.mark.jira_key("SHOP-1")
def test_products_table_exists(db_connection):

    cursor = db_connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='products'
    """)

    table = cursor.fetchone()

    assert table is not None


@pytest.mark.jira_key("SHOP-2")
def test_orders_table_exists(db_connection):

    cursor = db_connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='orders'
    """)

    table = cursor.fetchone()

    assert table is not None


# ================= INITIAL DATA TESTS ================= #

@pytest.mark.jira_key("SHOP-3")
def test_initial_products_inserted(db_connection):

    cursor = db_connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")

    count = cursor.fetchone()[0]

    # אמורים להיות לפחות 4 מוצרים התחלתיים
    assert count >= 4


@pytest.mark.jira_key("SHOP-4")
@pytest.mark.parametrize("product_name", [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Keyboard"
])
def test_initial_products_exist(db_connection, product_name):

    cursor = db_connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        (product_name,)
    )

    product = cursor.fetchone()

    assert product is not None


# ================= INSERT PRODUCT TESTS ================= #

@pytest.mark.jira_key("SHOP-5")
def test_insert_product(db_connection):

    cursor = db_connection.cursor()

    cursor.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        ("Monitor", 900, 7)
    )

    db_connection.commit()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        ("Monitor",)
    )

    product = cursor.fetchone()

    assert product is not None
    assert product["name"] == "Monitor"
    assert product["price"] == 900
    assert product["stock"] == 7


# ================= UPDATE PRODUCT TESTS ================= #

@pytest.mark.jira_key("SHOP-6")
def test_update_product_stock(db_connection):

    cursor = db_connection.cursor()

    cursor.execute(
        "UPDATE products SET stock = ? WHERE name = ?",
        (99, "Laptop")
    )

    db_connection.commit()

    cursor.execute(
        "SELECT stock FROM products WHERE name = ?",
        ("Laptop",)
    )

    updated_stock = cursor.fetchone()["stock"]

    assert updated_stock == 99


# ================= DELETE PRODUCT TESTS ================= #

@pytest.mark.jira_key("SHOP-7")
def test_delete_product(db_connection):

    cursor = db_connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE name = ?",
        ("Keyboard",)
    )

    db_connection.commit()

    cursor.execute(
        "SELECT * FROM products WHERE name = ?",
        ("Keyboard",)
    )

    deleted = cursor.fetchone()

    assert deleted is None


# ================= NEGATIVE TESTS ================= #

@pytest.mark.jira_key("SHOP-8")
def test_insert_product_without_name(db_connection):

    cursor = db_connection.cursor()

    with pytest.raises(Exception):

        cursor.execute(
            "INSERT INTO products (price, stock) VALUES (?, ?)",
            (100, 5)
        )

        db_connection.commit()


@pytest.mark.jira_key("SHOP-9")
def test_insert_negative_stock(db_connection):

    """
    בדיקה שממחישה באג אפשרי:
    המערכת מאפשרת מלאי שלילי
    """

    cursor = db_connection.cursor()

    cursor.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        ("Bug Product", 100, -10)
    )

    db_connection.commit()

    cursor.execute(
        "SELECT stock FROM products WHERE name = ?",
        ("Bug Product",)
    )

    stock = cursor.fetchone()["stock"]

    # כרגע זה עובר למרות שזה לא תקין עסקית
    assert stock == -10