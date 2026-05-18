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


# ================= HELPERS ================= #

def safe_json(res):
    """Avoid JSON crash on bad responses"""
    try:
        return res.json()
    except Exception:
        return {"raw": res.text}


# ================= GET PRODUCTS ================= #

def test_get_products(products_url):

    res = requests.get(products_url)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert isinstance(data, list)
    assert len(data) > 0

    for product in data:
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "stock" in product


def test_get_products_structure(products_url):

    res = requests.get(products_url)

    assert res.status_code == 200, safe_json(res)

    product = safe_json(res)[0]

    required_keys = ["id", "name", "price", "stock"]

    for key in required_keys:
        assert key in product


@pytest.mark.parametrize("index", [0, 1, 2])
def test_get_products_multiple(products_url, index):

    res = requests.get(products_url)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert data[index]["id"] > 0
    assert isinstance(data[index]["name"], str)


# ================= CHECKOUT ================= #

def test_checkout_positive(checkout_url):

    payload = {
        "cart": [{"id": 1, "quantity": 2}]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert data.get("status") == "success"
    assert data.get("total_paid") is not None
    assert data["total_paid"] > 0


@pytest.mark.parametrize("quantity", [1, 2, 5])
def test_checkout_multiple_quantities(checkout_url, quantity):

    payload = {
        "cart": [{"id": 1, "quantity": quantity}]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert data["status"] == "success"


def test_checkout_empty_cart(checkout_url):

    res = requests.post(checkout_url, json={"cart": []})

    assert res.status_code == 400, safe_json(res)

    data = safe_json(res)

    assert data["error"] == "Cart is empty"


def test_checkout_invalid_product(checkout_url):

    res = requests.post(checkout_url, json={
        "cart": [{"id": 999, "quantity": 1}]
    })

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert "status" in data


# ================= BUG TESTS ================= #

def test_checkout_negative_quantity_bug(checkout_url):

    payload = {
        "cart": [{"id": 1, "quantity": -5}]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    # BUG DETECTION
    assert data["total_paid"] < 0


def test_checkout_zero_quantity(checkout_url):

    payload = {
        "cart": [{"id": 1, "quantity": 0}]
    }

    res = requests.post(checkout_url, json=payload)

    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert data["total_paid"] == 0


# ================= END-TO-END FLOW ================= #

def test_full_shop_flow(products_url, checkout_url):

    res = requests.get(products_url)
    assert res.status_code == 200, safe_json(res)

    product = safe_json(res)[0]

    payload = {
        "cart": [
            {
                "id": product["id"],
                "quantity": 1
            }
        ]
    }

    res = requests.post(checkout_url, json=payload)
    assert res.status_code == 200, safe_json(res)

    data = safe_json(res)

    assert data["status"] == "success"
    assert data["total_paid"] == product["price"]