import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


@pytest.fixture
def driver():
    options = Options()

    # הטיפ החשוב: אם הקוד רץ בתוך GitHub Actions, המשתנה 'CI' קיים במערכת באופן אוטומטי
    if os.environ.get('CI'):
        options.add_argument('--headless')  # הרצה ללא מסך ויזואלי
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def test_add_to_cart_ui(driver):
    """בדיקת UI: מוודאת שהוספת מוצר לסל מעדכנת את הסכום הכללי במסך"""
    driver.get("http://127.0.0.1:5000")
    add_button = driver.find_element(By.CSS_SELECTOR, ".product-card .btn-success")
    add_button.click()
    total_price_element = driver.find_element(By.ID, "cart-total")
    assert total_price_element.text != "0.00", "המחיר במסך לא התעדכן לאחר הוספה לסל"