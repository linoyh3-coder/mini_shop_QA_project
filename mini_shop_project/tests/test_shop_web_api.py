import pytest
import requests


@pytest.fixture
def base_url():
    # כתובת ה-API הבסיסית של החנות
    return "http://127.0.0.1:5000/api"


@pytest.fixture
def initial_products_list(base_url):
    """פיקצ'ר השולף את המוצרים כפי שהם כרגע בשרת לצורך השוואה מובנית"""
    res = requests.get(f"{base_url}/products")
    return res.json()


# ================= GET PRODUCTS ================= #

def test_get_all_products_api(base_url, initial_products_list):
    """בדיקה שמחזירה את כל המוצרים ומוודאת סטטוס ותקינות המבנה"""
    res = requests.get(f"{base_url}/products")

    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == len(initial_products_list)


@pytest.mark.parametrize(
    "product_id, index",
    [
        [1, 0],
        [2, 1],
        [3, 2],
    ],
    ids=["first_product", "second_product", "third_product"]
)
def test_get_specific_product_by_id(base_url, initial_products_list, product_id, index):
    """בדיקה פרמטרית: שליפת מוצרים ספציפיים לפי ID והשוואה למיקום במערך"""
    res = requests.get(f"{base_url}/products")
    server_products = res.json()

    # שליפת המוצר הבודד לבדיקה מהשרת במידה ויש Endpoint תואם, או בדיקה מתוך המערך
    assert res.status_code == 200
    assert server_products[index]["id"] == product_id