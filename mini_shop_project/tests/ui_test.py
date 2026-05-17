import unittest
import uuid
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class MiniShopUITest(unittest.TestCase):

    def setUp(self):
        options = Options()
        # תמיכה בריצה חלקה ב-GitHub Actions
        if os.environ.get('CI'):
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 8)  # המתנה חכמה עד 8 שניות
        self.base_url = "http://127.0.0.1:5000"

    def tearDown(self):
        self.driver.quit()  # סגירת הדפדפן בסיום כל טסט

    # -------------------------------------------------
    # helpers (פונקציות עזר)
    # -------------------------------------------------
    def click_add_to_cart(self, product_name):
        """פונקציית עזר למציאת כפתור הוספה לסל לפי שם המוצר ולחיצה עליו"""
        product_element = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class, 'product-card')][.//h5[text()='{product_name}']]")
            )
        )
        add_button = product_element.find_element(By.CSS_SELECTOR, ".btn-success")
        self.safe_click(add_button)

    def safe_click(self, element):
        """קליק בטוח הכולל גלילה לאלמנט והמתנה שיהיה קליקבילי"""
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        self.wait.until(EC.element_to_be_clickable(element))
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    # -------------------------------------------------
    # 1. בדיקת דף הבית
    # -------------------------------------------------
    def test_homepage_loads(self):
        """בדיקה שהדף הראשי נטען וכותרת ה-h1 נכונה"""
        self.driver.get(self.base_url)

        # בדיקת כותרת הטאב בדפדפן
        self.assertIn("Mini Shop", self.driver.title)

        # המתנה לטקסט הראשי בחנות
        h1 = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertEqual(h1.text, "Products Catalog")

    # -------------------------------------------------
    # 2. בדיקת הוספה חוקית לסל
    # -------------------------------------------------
    def test_add_product_to_cart(self):
        """מוודא שהוספת מוצר קיים מעדכנת את ה-Total בעגלה"""
        self.driver.get(self.base_url)

        # הוספת מחשב נייד לסל באמצעות פונקציית העזר
        self.click_add_to_cart("Laptop")

        # וידוא שהסכום הכולל בעגלה השתנה ולא נשאר 0.00
        total_price_element = self.driver.find_element(By.ID, "cart-total")
        self.assertNotEqual(total_price_element.text, "0.00")


if __name__ == '__main__':
    unittest.main()