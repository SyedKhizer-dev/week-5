import unittest
from types import SimpleNamespace
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime

from app.controllers import order_controller
from app.models import Order


class TestOrderController(unittest.TestCase):

    @patch("app.controllers.order_controller.db.session")
    def test_create_order(self, mock_session):

        order_data = {
            "customer_id": 1,
            "order_date": datetime(2026, 11, 10, 10, 30),
            "ship_name": "Anna Bedecs",
            "shipping_fee": Decimal("25.5000"),
            "taxes": Decimal("10.0000"),
            "payment_type": "Credit Card",
            "status_id": 0,
        }

        order = order_controller.create_order(order_data)

        self.assertIsInstance(order, Order)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(order.payment_type, "Credit Card")

        mock_session.add.assert_called_once_with(order)
        mock_session.commit.assert_called_once()

    @patch("app.controllers.order_controller.db.session")
    def test_create_order_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        order_data = {"customer_id": 1, "payment_type": "Credit Card"}

        with self.assertRaises(Exception):
            order_controller.create_order(order_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()

    @patch("app.controllers.order_controller.db.session")
    def test_get_all_orders(self, mock_session):

        orders = [
            SimpleNamespace(id=30, customer_id=1),
            SimpleNamespace(id=31, customer_id=4),
        ]

        mock_session.execute.return_value.scalars.return_value.all.return_value = orders

        result = order_controller.get_all_orders()

        self.assertEqual(result, orders)
        self.assertEqual(len(result), 2)

        mock_session.execute.assert_called_once()

    @patch("app.controllers.order_controller.db.session")
    def test_get_order_by_id(self, mock_session):

        order = SimpleNamespace(id=30, customer_id=1)

        mock_session.get.return_value = order

        result = order_controller.get_order_by_id(30)

        self.assertEqual(result, order)
        mock_session.get.assert_called_once_with(Order, 30)

    @patch("app.controllers.order_controller.db.session")
    def test_get_order_by_id_not_found(self, mock_session):

        mock_session.get.return_value = None

        result = order_controller.get_order_by_id(999)

        self.assertIsNone(result)
        mock_session.get.assert_called_once_with(Order, 999)

    @patch("app.controllers.order_controller.db.session")
    def test_update_order(self, mock_session):

        order = SimpleNamespace(
            id=30,
            customer_id=1,
            payment_type="Credit Card",
            shipping_fee=Decimal("25.5000"),
        )

        order_data = {"payment_type": "Cash"}

        result = order_controller.update_order(order, order_data)

        self.assertEqual(result.payment_type, "Cash")
        self.assertEqual(result.shipping_fee, Decimal("25.5000"))

        mock_session.commit.assert_called_once()

    @patch("app.controllers.order_controller.db.session")
    def test_update_order_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        order = SimpleNamespace(id=30, customer_id=1, payment_type="Credit Card")

        with self.assertRaises(Exception):
            order_controller.update_order(order, {"payment_type": "Cash"})

        mock_session.rollback.assert_called_once()

    @patch("app.controllers.order_controller.db.session")
    def test_get_customer_order_history(self, mock_session):

        orders = [
            SimpleNamespace(id=30, customer_id=27),
            SimpleNamespace(id=31, customer_id=27),
        ]

        mock_session.execute.return_value.scalars.return_value.all.return_value = orders

        result = order_controller.get_customer_order_history(27)

        self.assertEqual(result, orders)
        self.assertEqual(len(result), 2)

        mock_session.execute.assert_called_once()

        query = mock_session.execute.call_args.args[0]

        self.assertIn("orders.customer_id =", str(query))

        self.assertIn("ORDER BY orders.order_date DESC", str(query))


if __name__ == "__main__":
    unittest.main()
