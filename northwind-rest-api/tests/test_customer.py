import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import create_app


def make_customer(
    id=1,
    company="Company A",
    first_name="Anna",
    last_name="Bedecs",
    email_address=None,
    job_title="Owner",
    business_phone="1234567890",
    city="Seattle",
    country_region="USA",
):
    return SimpleNamespace(
        id=id,
        company=company,
        first_name=first_name,
        last_name=last_name,
        email_address=email_address,
        job_title=job_title,
        business_phone=business_phone,
        city=city,
        country_region=country_region,
    )


class TestCustomerRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app()
        self.app.config["TESTING"] = True

        self.client = self.app.test_client()

    @patch("app.routes.customer_routes.customer_controller.create_customer")
    def test_create_customer(self, mock_create):

        payload = {
            "company": "Test Company",
            "first_name": "Khizer",
            "last_name": "Syed",
            "email_address": "khizer@example.com",
            "job_title": "Developer",
            "business_phone": "9876543210",
            "city": "Bengaluru",
            "country_region": "India",
        }

        customer = make_customer(id=30, **payload)

        mock_create.return_value = customer

        response = self.client.post("/api/customers", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 30)
        self.assertEqual(response.get_json()["first_name"], "Khizer")

        mock_create.assert_called_once_with(payload)

    @patch("app.routes.customer_routes.customer_controller.get_all_customers")
    def test_get_all_customers(self, mock_get_all):

        customers = [
            make_customer(id=1),
            make_customer(id=2, company="Company B", first_name="Antonio"),
        ]

        mock_get_all.return_value = customers

        response = self.client.get("/api/customers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertEqual(response.get_json()[0]["first_name"], "Anna")
        self.assertEqual(response.get_json()[1]["first_name"], "Antonio")

        mock_get_all.assert_called_once()

    @patch("app.routes.customer_routes.customer_controller.get_customer_by_id")
    def test_get_customer_by_id(self, mock_get):

        mock_get.return_value = make_customer(id=1)

        response = self.client.get("/api/customers/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 1)
        self.assertEqual(response.get_json()["company"], "Company A")

        mock_get.assert_called_once_with(1)

    @patch("app.routes.customer_routes.customer_controller.get_customer_by_id")
    def test_get_customer_not_found(self, mock_get):

        mock_get.return_value = None

        response = self.client.get("/api/customers/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Customer not found")

    @patch("app.routes.customer_routes.customer_controller.update_customer")
    @patch("app.routes.customer_routes.customer_controller.get_customer_by_id")
    def test_update_customer(self, mock_get, mock_update):

        customer = make_customer(id=1, city="Seattle")

        updated_customer = make_customer(id=1, city="Mysuru")

        mock_get.return_value = customer
        mock_update.return_value = updated_customer

        response = self.client.patch("/api/customers/1", json={"city": "Mysuru"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["city"], "Mysuru")

        mock_get.assert_called_once_with(1)
        mock_update.assert_called_once_with(customer, {"city": "Mysuru"})

    @patch("app.routes.customer_routes.customer_controller.create_customer")
    def test_create_customer_invalid_data(self, mock_create):

        payload = {"company": "A" * 51, "first_name": "John"}

        response = self.client.post("/api/customers", json=payload)

        self.assertEqual(response.status_code, 400)
        mock_create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
