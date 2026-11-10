import unittest
from types import SimpleNamespace
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime

from app import create_app


def make_order(
    id=30,
    customer_id=1,
    order_date=None,
    shipped_date=None,
    ship_name="Anna Bedecs",
    shipping_fee=Decimal("25.5000"),
    taxes=Decimal("10.0000"),
    payment_type="Credit Card",
    status_id=0,
    order_details=None,
):
    return SimpleNamespace(
        id=id,
        customer_id=customer_id,
        order_date=order_date,
        shipped_date=shipped_date,
        ship_name=ship_name,
        shipping_fee=shipping_fee,
        taxes=taxes,
        payment_type=payment_type,
        status_id=status_id,
        order_details=order_details or [],
    )


def make_order_detail():

    return SimpleNamespace(
        id=27,
        order_id=30,
        product_id=34,
        quantity=Decimal("2.0000"),
        unit_price=Decimal("18.0000"),
        discount=0.0,
        date_allocated=None,
    )


class TestOrderRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app()
        self.app.config["TESTING"] = True

        self.client = self.app.test_client()

    @patch("app.routes.order_routes.order_controller.create_order")
    def test_create_order(self, mock_create):

        payload = {
            "customer_id": 1,
            "order_date": "2026-11-10T10:30:00",
            "ship_name": "Anna Bedecs",
            "shipping_fee": 25.50,
            "taxes": 10.00,
            "payment_type": "Credit Card",
            "status_id": 0,
        }

        order = make_order(
            id=49, customer_id=1, order_date=datetime(2026, 11, 10, 10, 30)
        )

        mock_create.return_value = order

        response = self.client.post("/api/orders", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 49)
        self.assertEqual(response.get_json()["customer_id"], 1)

        mock_create.assert_called_once()

    @patch("app.routes.order_routes.order_controller.get_all_orders")
    def test_get_all_orders(self, mock_get_all):

        orders = [
            make_order(id=30),
            make_order(id=31, customer_id=4, payment_type="Cash"),
        ]

        mock_get_all.return_value = orders

        response = self.client.get("/api/orders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertEqual(response.get_json()[0]["id"], 30)
        self.assertEqual(response.get_json()[1]["id"], 31)

        mock_get_all.assert_called_once()

    @patch("app.routes.order_routes.order_controller.get_order_by_id")
    def test_get_order_by_id(self, mock_get):

        mock_get.return_value = make_order(id=30)

        response = self.client.get("/api/orders/30")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 30)
        self.assertEqual(response.get_json()["customer_id"], 1)

        mock_get.assert_called_once_with(30)

    @patch("app.routes.order_routes.order_controller.get_order_by_id")
    def test_get_order_not_found(self, mock_get):

        mock_get.return_value = None

        response = self.client.get("/api/orders/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Order not found")

    @patch("app.routes.order_routes.order_controller.update_order")
    @patch("app.routes.order_routes.order_controller.get_order_by_id")
    def test_update_order(self, mock_get, mock_update):

        order = make_order(id=30)

        updated_order = make_order(id=30, payment_type="Cash")

        mock_get.return_value = order
        mock_update.return_value = updated_order

        response = self.client.patch("/api/orders/30", json={"payment_type": "Cash"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["payment_type"], "Cash")

        mock_get.assert_called_once_with(30)
        mock_update.assert_called_once_with(order, {"payment_type": "Cash"})

    @patch("app.routes.order_routes.order_controller.create_order")
    def test_create_order_invalid_shipping_fee(self, mock_create):

        payload = {"customer_id": 1, "shipping_fee": -100}

        response = self.client.post("/api/orders", json=payload)

        self.assertEqual(response.status_code, 400)
        mock_create.assert_not_called()

    @patch("app.routes.order_routes.order_controller.get_customer_order_history")
    def test_get_customer_order_history(self, mock_history):

        order = make_order(id=30, customer_id=27, order_details=[make_order_detail()])

        mock_history.return_value = [order]

        response = self.client.get("/api/customers/27/orders")

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()

        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["customer_id"], 27)
        self.assertEqual(len(response_data[0]["order_details"]), 1)
        self.assertEqual(response_data[0]["order_details"][0]["product_id"], 34)

        mock_history.assert_called_once_with(27)

    @patch("app.routes.order_routes.order_controller.get_customer_order_history")
    def test_customer_order_history_empty(self, mock_history):

        mock_history.return_value = []

        response = self.client.get("/api/customers/999/orders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

        mock_history.assert_called_once_with(999)


if __name__ == "__main__":
    unittest.main()
