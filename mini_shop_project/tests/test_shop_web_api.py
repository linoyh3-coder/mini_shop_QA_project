import pytest
import requests


# ================= FIXTURES ================= #

@pytest.fixture
def base_url():
    return "http://127.0.0.1:5000"


@pytest.fixture
def products_url(base_url):
    return f"{base_url}/products"


@pytest.fixture
def checkout_url(base_url):
    return f"{base_url}/checkout"


# ================= GET PRODUCTS ================= #

def test_get_products(products_url):

    res = requests.get(products_url)

    assert res.status_code == 200
    assert res.reason == "OK"

    data = res.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_get_products_structure(products_url):

    res = requests.get(products_url)

    product = res.json()[0]

    assert "id" in product
    assert "name" in product
    assert "price" in product
    assert "stock" in product


@pytest.mark.parametrize(
    "index",
    [0, 1, 2]
)
def test_get_products_multiple(products_url, index):

    res = requests.get(products_url)

    data = res.json()

    assert data[index]["id"] > 0
    assert isinstance(data[index]["name"], str)


# ================= CHECKOUT ================= #

def test_checkout_positive(checkout_url):

    payload = {
        "cart": [
            {
                "id": 1,
                "quantity": 2
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200
    assert res.reason == "OK"

    data = res.json()

    assert data["status"] == "success"
    assert data["total_paid"] > 0


@pytest.mark.parametrize(
    "quantity",
    [1, 2, 5]
)
def test_checkout_multiple_quantities(checkout_url, quantity):

    payload = {
        "cart": [
            {
                "id": 1,
                "quantity": quantity
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200

    data = res.json()

    assert data["status"] == "success"


# ================= NEGATIVE TESTS ================= #

def test_checkout_empty_cart(checkout_url):

    payload = {
        "cart": []
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 400
    assert res.reason == "BAD REQUEST"

    assert res.json()["error"] == "Cart is empty"


def test_checkout_invalid_product(checkout_url):

    payload = {
        "cart": [
            {
                "id": 999,
                "quantity": 1
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    # כרגע המערכת עדיין מחזירה success
    assert res.status_code == 200

    data = res.json()

    assert data["status"] == "success"
    assert data["total_paid"] == 0


# ================= BUG TESTS ================= #

def test_checkout_negative_quantity_bug(checkout_url):

    """
    הבדיקה מדגימה את הבאג:
    ניתן לשלוח quantity שלילי
    """

    payload = {
        "cart": [
            {
                "id": 1,
                "quantity": -5
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    # הבקשה עדיין מצליחה
    assert res.status_code == 200

    data = res.json()

    # BUG:
    # total_paid נהיה שלילי
    assert data["total_paid"] < 0


def test_checkout_zero_quantity(checkout_url):

    payload = {
        "cart": [
            {
                "id": 1,
                "quantity": 0
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200

    data = res.json()

    assert data["total_paid"] == 0


# ================= FLOW TEST ================= #

def test_full_shop_flow(base_url, products_url, checkout_url):

    # Step 1 - Get products
    res = requests.get(products_url)

    assert res.status_code == 200

    products = res.json()

    first_product = products[0]

    # Step 2 - Checkout
    payload = {
        "cart": [
            {
                "id": first_product["id"],
                "quantity": 1
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200

    data = res.json()

    # Step 3 - Verify response
    assert data["status"] == "success"
    assert data["total_paid"] == first_product["price"]