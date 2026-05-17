# בדיקות אך ורק לשכבת ה-Controller (ה-API)
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/api"


def test_get_products_endpoint():
    """בדיקת API: מוודאת שכתובת ה-Products מחזירה קוד 200 ומערך נתונים"""
    response = requests.get(f"{BASE_URL}/products")

    assert response.status_code == 200, f"צפוי 200 אך התקבל {response.status_code}"
    assert isinstance(response.json(), list), "התגובה מה-API חייבת להיות מערך (List)"