import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestMiniShopUI(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 8)
        self.base_url = "http://localhost:5000"

    def tearDown(self):
        self.driver.quit()

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def add_first_product_to_cart(self):

        add_buttons = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "btn-success")
            )
        )

        add_buttons[0].click()

    # -------------------------------------------------
    # 1. Homepage
    # -------------------------------------------------

    def test_homepage(self):

        self.driver.get(self.base_url)

        self.assertIn("Mini Shop", self.driver.title)

        h1 = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        self.assertIn("Mini Shop", h1.text)

    # -------------------------------------------------
    # 2. Products Loaded
    # -------------------------------------------------

    def test_products_loaded(self):

        self.driver.get(self.base_url)

        products = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "product-card")
            )
        )

        self.assertGreater(len(products), 0)

    # -------------------------------------------------
    # 3. Add Product To Cart
    # -------------------------------------------------

    def test_add_product_to_cart(self):

        self.driver.get(self.base_url)

        self.add_first_product_to_cart()

        cart_items = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "#cart-list li")
            )
        )

        self.assertGreater(len(cart_items), 0)

    # -------------------------------------------------
    # 4. Cart Total Updated
    # -------------------------------------------------

    def test_cart_total_updated(self):

        self.driver.get(self.base_url)

        self.add_first_product_to_cart()

        total = self.driver.find_element(By.ID, "cart-total")

        self.assertNotEqual("0.00", total.text)

    # -------------------------------------------------
    # 5. Empty Cart Message
    # -------------------------------------------------

    def test_empty_cart_message(self):

        self.driver.get(self.base_url)

        cart_text = self.driver.find_element(
            By.ID,
            "cart-list"
        ).text

        self.assertIn("העגלה שלך ריקה", cart_text)

    # -------------------------------------------------
    # 6. Checkout Alert
    # -------------------------------------------------

    def test_checkout_alert(self):

        self.driver.get(self.base_url)

        self.add_first_product_to_cart()

        checkout_btn = self.driver.find_element(
            By.ID,
            "checkout-btn"
        )

        checkout_btn.click()

        alert = self.wait.until(
            EC.alert_is_present()
        )

        self.assertIn("הזמנתך בוצעה", alert.text)

        alert.accept()

    # -------------------------------------------------
    # 7. Cart Cleared After Checkout
    # -------------------------------------------------

    def test_cart_cleared_after_checkout(self):

        self.driver.get(self.base_url)

        self.add_first_product_to_cart()

        checkout_btn = self.driver.find_element(
            By.ID,
            "checkout-btn"
        )

        checkout_btn.click()

        alert = self.wait.until(
            EC.alert_is_present()
        )

        alert.accept()

        cart_text = self.driver.find_element(
            By.ID,
            "cart-list"
        ).text

        self.assertIn("העגלה שלך ריקה", cart_text)

    # -------------------------------------------------
    # 8. BUG TEST - Stock Not Updated
    # -------------------------------------------------

    def test_bug_checkout_does_not_update_stock(self):

        """
        הבדיקה מדגימה את הבאג:
        ה־Frontend מנקה את העגלה
        אבל בכלל לא קורא לשרת
        """

        self.driver.get(self.base_url)

        # שמירת טקסט המלאי לפני רכישה
        stock_before = self.driver.find_element(
            By.CLASS_NAME,
            "product-info"
        ).text

        # הוספה לסל
        self.add_first_product_to_cart()

        # Checkout
        checkout_btn = self.driver.find_element(
            By.ID,
            "checkout-btn"
        )

        checkout_btn.click()

        alert = self.wait.until(
            EC.alert_is_present()
        )

        alert.accept()

        # רענון עמוד
        self.driver.refresh()

        self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "product-card")
            )
        )

        # בדיקת מלאי מחדש
        stock_after = self.driver.find_element(
            By.CLASS_NAME,
            "product-info"
        ).text

        # הבאג: המלאי לא השתנה
        self.assertEqual(stock_before, stock_after)


if __name__ == "__main__":
    unittest.main()