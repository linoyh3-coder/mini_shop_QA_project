# בדיקות לשכבת ה-Service (לוגיקה מתמטית ועסקית)
import pytest
from unittest.mock import patch, MagicMock
from app.services.shop_service import ShopService


def test_process_checkout_logic_calculation():
    """בדיקת לוגיקה: מוודאת שחישוב המחיר הכולל בשירות תקין באמצעות Mock ל-DB"""

    # אנחנו עושים patch לפונקציה שמחברת ל-DB האמיתי בתוך קובץ ה-service
    with patch('app.services.shop_service.get_db_connection') as mock_get_db:
        # יצירת חיבור פיקטיבי ומריץ שאילתות פיקטיבי (Mock)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # נדמה מוצר פיקטיבי שה-DB כביכול מחזיר (id=1, name='Test', price=100.0, stock=5)
        mock_cursor.execute.return_value.fetchone.return_value = {'id': 1, 'name': 'Test', 'price': 100.0, 'stock': 5}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        # הרצת הפונקציה של ה-Service עם עגלה מדומה (קניית 2 יחידות)
        fake_cart = [{"id": 1, "quantity": 2}]
        result = ShopService.process_checkout(fake_cart)

        # בדיקה: 2 יחידות כפול 100 ש"ח אמורות לתת בדיוק 200.0 ש"ח סה"כ
        assert result["total_paid"] == 200.0, f"הלוגיקה חישבה {result['total_paid']} במקום 200.0"