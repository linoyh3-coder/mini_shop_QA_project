import unittest
from unittest.mock import patch, Mock
# ייבוא שכבת ה-Service של החנות שלנו
import app.services.shop_service as service


class TestShopService(unittest.TestCase):

    # ============== Checkout - Positive Tests ============== #

    @patch("app.services.shop_service.get_db_connection")  # החלפת פונקציית החיבור ל-DB בחיבור מדומה
    def test_process_checkout_positive(self, mock_get_db: Mock):
        # Arrange - יצירת מוקים מדומים של חיבור וקורסור
        mock_conn = Mock()
        mock_cursor = Mock()

        # דימוי של מוצר תקין שחוזר מה-DB בעת בדיקת מלאי (id=1, name='Laptop', price=1000.0, stock=10)
        mock_cursor.fetchone.return_value = {'id': 1, 'name': 'Laptop', 'price': 1000.0, 'stock': 10}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        # Act - הפעלת פונקציית הרכישה בשירות עבור 2 יחידות של מוצר 1
        fake_cart = [{"id": 1, "quantity": 2}]
        result = service.ShopService.process_checkout(fake_cart)

        # Assert - חישוב מתמטי טהור: 2 יחידות כפול 1000 ש"ח שווה 2000.0 ש"ח
        self.assertEqual(result["total_paid"], 2000.0)

        # Validation - וידוא שהפונקציה ביצעה בדיקת מלאי וקראה ל-DB לפחות פעם אחת
        self.assertTrue(mock_cursor.execute.called)

    # ============== Checkout - Negative Tests ============== #

    @patch("app.services.shop_service.get_db_connection")
    def test_checkout_insufficient_stock(self, mock_get_db: Mock):
        # Arrange - נדמה מוצר שהמלאי שלו ב-DB הוא רק 2 יחידות
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {'id': 1, 'name': 'Laptop', 'price': 1000.0, 'stock': 2}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        # Act + Assert - ניסיון לקנות 5 יחידות כשיש רק 2 אמור לזרוק חריגה (Exception)
        fake_cart = [{"id": 1, "quantity": 5}]

        with self.assertRaises(Exception):
            service.ShopService.process_checkout(fake_cart)


if __name__ == '__main__':
    unittest.main()