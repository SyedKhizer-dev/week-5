import unittest
from types import SimpleNamespace
from unittest.mock import patch
from decimal import Decimal

from app.controllers import product_controller
from app.models import Product


class TestProductController(unittest.TestCase):

    @patch("app.controllers.product_controller.db.session")
    def test_create_product(self, mock_session):

        product_data = {
            "product_code": "PRD-101",
            "product_name": "Wireless Mouse",
            "standard_cost": Decimal("250.0000"),
            "list_price": Decimal("499.0000"),
            "discontinued": False,
            "category": "Electronics",
        }

        product = product_controller.create_product(product_data)

        self.assertIsInstance(product, Product)
        self.assertEqual(product.product_name, "Wireless Mouse")
        self.assertEqual(product.list_price, Decimal("499.0000"))

        mock_session.add.assert_called_once_with(product)
        mock_session.commit.assert_called_once()

    @patch("app.controllers.product_controller.db.session")
    def test_create_product_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        product_data = {
            "product_name": "Wireless Mouse",
            "list_price": Decimal("499.0000"),
        }

        with self.assertRaises(Exception):
            product_controller.create_product(product_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()

    @patch("app.controllers.product_controller.db.session")
    def test_get_all_products(self, mock_session):

        products = [
            SimpleNamespace(id=1, product_name="Wireless Mouse"),
            SimpleNamespace(id=2, product_name="Wireless Keyboard"),
        ]

        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            products
        )

        result = product_controller.get_all_products()

        self.assertEqual(result, products)
        self.assertEqual(len(result), 2)

        mock_session.execute.assert_called_once()

    @patch("app.controllers.product_controller.db.session")
    def test_get_product_by_id(self, mock_session):

        product = SimpleNamespace(id=1, product_name="Wireless Mouse")

        mock_session.get.return_value = product

        result = product_controller.get_product_by_id(1)

        self.assertEqual(result, product)
        mock_session.get.assert_called_once_with(Product, 1)

    @patch("app.controllers.product_controller.db.session")
    def test_get_product_by_id_not_found(self, mock_session):

        mock_session.get.return_value = None

        result = product_controller.get_product_by_id(999)

        self.assertIsNone(result)
        mock_session.get.assert_called_once_with(Product, 999)

    @patch("app.controllers.product_controller.db.session")
    def test_update_product(self, mock_session):

        product = SimpleNamespace(
            id=1, product_name="Wireless Mouse", list_price=Decimal("499.0000")
        )

        product_data = {"list_price": Decimal("599.0000")}

        result = product_controller.update_product(product, product_data)

        self.assertEqual(result.list_price, Decimal("599.0000"))
        self.assertEqual(result.product_name, "Wireless Mouse")

        mock_session.commit.assert_called_once()

    @patch("app.controllers.product_controller.db.session")
    def test_update_product_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        product = SimpleNamespace(
            id=1, product_name="Wireless Mouse", list_price=Decimal("499.0000")
        )

        with self.assertRaises(Exception):
            product_controller.update_product(
                product, {"list_price": Decimal("599.0000")}
            )

        mock_session.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
