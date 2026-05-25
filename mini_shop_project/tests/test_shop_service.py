from unittest import TestCase
from unittest.mock import patch, Mock

import app.services.shop_service
from app.services.shop_service import ShopService


class TestShopService(TestCase):

    # ============== Get All Products - Positive Tests ============== #

    @patch("app.services.shop_service.get_db_connection")
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


    @patch("app.services.shop_service.get_db_connection")
    def test_get_all_products_empty_list(self, mock_get_db_connection: Mock):

        mock_conn = Mock()

        mock_conn.execute.return_value.fetchall.return_value =  []

        mock_get_db_connection.return_value = mock_conn

        result = ShopService.get_all_products()

        self.assertEqual([], result)

        mock_conn.execute.assert_called_once_with("SELECT * FROM products")
        mock_conn.close.assert_called_once()


    @patch("app.services.shop_service.get_db_connection")
    def test_get_all_products_returns_dicts(self, mock_get_db_connection: Mock):
        mock_conn = Mock()

        mock_products = [
            {'id': 1, 'name': 'keyboard', 'price': 200, 'stock': 10}
        ]

        mock_conn.execute.return_value.fetchall.return_value = mock_products
        mock_get_db_connection.return_value = mock_conn

        result = ShopService.get_all_products()

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)

        mock_conn.execute.assert_called_once()


    # ============== Get All Products - Negative Tests ============== #

    @patch("app.services.shop_service.get_db_connection")
    def test_get_all_products_closes_connection_on_exception(self, mock_get_db_connection: Mock):

        mock_conn = Mock()

        mock_conn.execute.side_effect = Exception("data base error!")

        mock_get_db_connection.return_value = mock_conn

        with self.assertRaises(Exception):
            ShopService.get_all_products()

        mock_conn.close.assert_called_once()


    @patch("app.services.shop_service.get_db_connection")
    def test_get_all_products_db_error(self, mock_get_db_connection: Mock):
        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("DB error")

        mock_get_db_connection.return_value = mock_conn

        with self.assertRaises(Exception):
            ShopService.get_all_products()

        mock_conn.close.assert_called_once()


    # ============== Checkout - Positive Tests ============== #

    @patch("app.services.shop_service.get_db_connection")
    def test_process_checkout_positive(self, mock_get_db_connection: Mock):

        mock_conn = Mock()
        mock_cursor = Mock()

        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.return_value.fetchone.side_effect = [
            {'id':1, 'name':'Laptop', 'price':3000, 'stock': 5}
        ]

        mock_get_db_connection.return_value = mock_conn

        cart = [
            {'id': 1, 'quantity': 2}
        ]

        result = ShopService.process_checkout(cart)

        expected_total = 3000 * 2

        self.assertEqual("success", result['status'])
        self.assertEqual(expected_total, result['total_paid'])

        mock_conn.commit.assert_called_once()


    # ============== Checkout - Multiple Products ============== #

    @patch("app.services.shop_service.get_db_connection")
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

    @patch("app.services.shop_service.get_db_connection")
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

    @patch("app.services.shop_service.get_db_connection")
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

    @patch("app.services.shop_service.get_db_connection")
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

    @patch("app.services.shop_service.get_db_connection")
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