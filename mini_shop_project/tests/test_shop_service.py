from unittest import TestCase
from unittest.mock import patch, Mock

from app.shop_service import ShopService


class TestShopService(TestCase):

    # ============== Get All Products - Positive Tests ============== #

    @patch("app.shop_service.get_db_connection")
    def test_get_all_products_positive(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()

        mock_conn.execute.return_value.fetchall.return_value = [
            {'id': 1, 'name': 'Laptop', 'price': 3000, 'stock': 5},
            {'id': 2, 'name': 'Mouse', 'price': 150, 'stock': 20}
        ]

        mock_get_db_connection.return_value = mock_conn

        # Act
        result = ShopService.get_all_products()

        # Assert
        self.assertEqual(2, len(result))
        self.assertEqual("Laptop", result[0]['name'])
        self.assertEqual("Mouse", result[1]['name'])

        # Validation
        mock_conn.execute.assert_called_once_with("SELECT * FROM products")
        mock_conn.close.assert_called_once()


    # ============== Checkout - Positive Tests ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_positive(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        # מוצר שקיים במלאי
        mock_cursor.execute.return_value.fetchone.return_value = {
            'id': 1,
            'name': 'Laptop',
            'price': 3000,
            'stock': 10
        }

        mock_get_db_connection.return_value = mock_conn

        cart = [
            {'id': 1, 'quantity': 2}
        ]

        # Act
        result = ShopService.process_checkout(cart)

        # Assert
        self.assertEqual("success", result['status'])
        self.assertEqual(6000, result['total_paid'])

        # Validation
        self.assertEqual(2, mock_cursor.execute.call_count)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


    # ============== Checkout - Multiple Products ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_multiple_products(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        # מחזירים מוצרים שונים לפי סדר הקריאות
        mock_cursor.execute.return_value.fetchone.side_effect = [
            {'id': 1, 'name': 'Laptop', 'price': 3000, 'stock': 10},
            {'id': 2, 'name': 'Mouse', 'price': 200, 'stock': 50}
        ]

        mock_get_db_connection.return_value = mock_conn

        cart = [
            {'id': 1, 'quantity': 1},
            {'id': 2, 'quantity': 3}
        ]

        # Act
        result = ShopService.process_checkout(cart)

        # Assert
        expected_total = 3000 + (200 * 3)

        self.assertEqual("success", result['status'])
        self.assertEqual(expected_total, result['total_paid'])

        # Validation
        mock_conn.commit.assert_called_once()


    # ============== Checkout - Product Not Found ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_product_not_found(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        # מוצר לא קיים
        mock_cursor.execute.return_value.fetchone.return_value = None

        mock_get_db_connection.return_value = mock_conn

        cart = [
            {'id': 999, 'quantity': 2}
        ]

        # Act
        result = ShopService.process_checkout(cart)

        # Assert
        self.assertEqual("success", result['status'])
        self.assertEqual(0, result['total_paid'])

        # Validation
        mock_conn.commit.assert_called_once()


    # ============== Checkout - Boundary Tests ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_different_quantities(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.return_value.fetchone.return_value = {
            'id': 1,
            'name': 'Keyboard',
            'price': 250,
            'stock': 100
        }

        mock_get_db_connection.return_value = mock_conn

        quantities = [1, 5, 10, 50]

        for qty in quantities:

            cart = [{'id': 1, 'quantity': qty}]

            # Act
            result = ShopService.process_checkout(cart)

            # Assert
            self.assertEqual("success", result['status'])
            self.assertEqual(250 * qty, result['total_paid'])

        # Validation
        self.assertEqual(8, mock_cursor.execute.call_count)


    # ============== Checkout - Negative Stock Bug Test ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_negative_stock_bug(self, mock_get_db_connection: Mock):

        """
        בדיקה שממחישה את הבאג:
        ניתן לקנות יותר פריטים ממה שיש במלאי
        והמלאי נהיה שלילי
        """

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        # במלאי יש רק 2
        mock_cursor.execute.return_value.fetchone.return_value = {
            'id': 1,
            'name': 'Phone',
            'price': 2000,
            'stock': 2
        }

        mock_get_db_connection.return_value = mock_conn

        cart = [
            {'id': 1, 'quantity': 5}
        ]

        # Act
        result = ShopService.process_checkout(cart)

        # Assert
        self.assertEqual("success", result['status'])
        self.assertEqual(10000, result['total_paid'])

        # Validation
        # הבאג: המלאי נהיה מינוס 3
        mock_cursor.execute.assert_any_call(
            "UPDATE products SET stock = ? WHERE id = ?",
            (-3, 1)
        )

        mock_conn.commit.assert_called_once()


    # ============== Checkout - Empty Cart ============== #

    @patch("app.shop_service.get_db_connection")
    def test_process_checkout_empty_cart(self, mock_get_db_connection: Mock):

        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        mock_get_db_connection.return_value = mock_conn

        cart = []

        # Act
        result = ShopService.process_checkout(cart)

        # Assert
        self.assertEqual("success", result['status'])
        self.assertEqual(0, result['total_paid'])

        # Validation
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()