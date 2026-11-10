import unittest
from types import SimpleNamespace
from unittest.mock import patch
from decimal import Decimal

from app import create_app


def make_product(
    id=1,
    product_code="PRD-101",
    product_name="Wireless Mouse",
    description="Wireless optical mouse",
    standard_cost=Decimal("250.0000"),
    list_price=Decimal("499.0000"),
    reorder_level=10,
    target_level=50,
    quantity_per_unit="1 piece",
    discontinued=False,
    category="Electronics",
):
    return SimpleNamespace(
        id=id,
        product_code=product_code,
        product_name=product_name,
        description=description,
        standard_cost=standard_cost,
        list_price=list_price,
        reorder_level=reorder_level,
        target_level=target_level,
        quantity_per_unit=quantity_per_unit,
        discontinued=discontinued,
        category=category,
    )


class TestProductRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app()
        self.app.config["TESTING"] = True

        self.client = self.app.test_client()

    @patch("app.routes.product_routes.product_controller.create_product")
    def test_create_product(self, mock_create):

        payload = {
            "product_code": "PRD-101",
            "product_name": "Wireless Mouse",
            "description": "Wireless optical mouse",
            "standard_cost": 250.00,
            "list_price": 499.00,
            "reorder_level": 10,
            "target_level": 50,
            "quantity_per_unit": "1 piece",
            "discontinued": False,
            "category": "Electronics",
        }

        product = make_product(id=46)

        mock_create.return_value = product

        response = self.client.post("/api/products", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 46)
        self.assertEqual(response.get_json()["product_name"], "Wireless Mouse")

        mock_create.assert_called_once()

    @patch("app.routes.product_routes.product_controller.get_all_products")
    def test_get_all_products(self, mock_get_all):

        products = [
            make_product(id=1),
            make_product(
                id=2, product_name="Wireless Keyboard", list_price=Decimal("799.0000")
            ),
        ]

        mock_get_all.return_value = products

        response = self.client.get("/api/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertEqual(response.get_json()[0]["product_name"], "Wireless Mouse")

        mock_get_all.assert_called_once()

    @patch("app.routes.product_routes.product_controller.get_product_by_id")
    def test_get_product_by_id(self, mock_get):

        mock_get.return_value = make_product(id=1)

        response = self.client.get("/api/products/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 1)
        self.assertEqual(response.get_json()["product_name"], "Wireless Mouse")

        mock_get.assert_called_once_with(1)

    @patch("app.routes.product_routes.product_controller.get_product_by_id")
    def test_get_product_not_found(self, mock_get):

        mock_get.return_value = None

        response = self.client.get("/api/products/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Product not found")

    @patch("app.routes.product_routes.product_controller.update_product")
    @patch("app.routes.product_routes.product_controller.get_product_by_id")
    def test_update_product(self, mock_get, mock_update):

        product = make_product(id=1)

        updated_product = make_product(id=1, list_price=Decimal("599.0000"))

        mock_get.return_value = product
        mock_update.return_value = updated_product

        response = self.client.patch("/api/products/1", json={"list_price": 599.00})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["list_price"], "599.0000")

        mock_get.assert_called_once_with(1)
        mock_update.assert_called_once_with(product, {"list_price": Decimal("599.00")})

    @patch("app.routes.product_routes.product_controller.create_product")
    def test_create_product_invalid_price(self, mock_create):

        payload = {"product_name": "Wireless Mouse", "list_price": -100}

        response = self.client.post("/api/products", json=payload)

        self.assertEqual(response.status_code, 400)
        mock_create.assert_not_called()

    @patch("app.routes.product_routes.product_controller.create_product")
    def test_create_product_missing_price(self, mock_create):

        payload = {"product_name": "Wireless Mouse"}

        response = self.client.post("/api/products", json=payload)

        self.assertEqual(response.status_code, 400)
        mock_create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
