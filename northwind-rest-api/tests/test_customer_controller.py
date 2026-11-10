import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.controllers import customer_controller
from app.models import Customer


class TestCustomerController(unittest.TestCase):

    @patch("app.controllers.customer_controller.db.session")
    def test_create_customer(self, mock_session):

        customer_data = {
            "company": "Test Company",
            "first_name": "Khizer",
            "last_name": "Syed",
            "city": "Bengaluru",
        }

        customer = customer_controller.create_customer(customer_data)

        self.assertIsInstance(customer, Customer)
        self.assertEqual(customer.company, "Test Company")
        self.assertEqual(customer.first_name, "Khizer")

        mock_session.add.assert_called_once_with(customer)
        mock_session.commit.assert_called_once()

    @patch("app.controllers.customer_controller.db.session")
    def test_create_customer_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        customer_data = {"company": "Test Company", "first_name": "Khizer"}

        with self.assertRaises(Exception):
            customer_controller.create_customer(customer_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()

    @patch("app.controllers.customer_controller.db.session")
    def test_get_all_customers(self, mock_session):

        customers = [
            SimpleNamespace(id=1, company="Company A"),
            SimpleNamespace(id=2, company="Company B"),
        ]

        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            customers
        )

        result = customer_controller.get_all_customers()

        self.assertEqual(result, customers)
        self.assertEqual(len(result), 2)

        mock_session.execute.assert_called_once()

    @patch("app.controllers.customer_controller.db.session")
    def test_get_customer_by_id(self, mock_session):

        customer = SimpleNamespace(id=1, company="Company A")

        mock_session.get.return_value = customer

        result = customer_controller.get_customer_by_id(1)

        self.assertEqual(result, customer)
        mock_session.get.assert_called_once_with(Customer, 1)

    @patch("app.controllers.customer_controller.db.session")
    def test_get_customer_by_id_not_found(self, mock_session):

        mock_session.get.return_value = None

        result = customer_controller.get_customer_by_id(999)

        self.assertIsNone(result)
        mock_session.get.assert_called_once_with(Customer, 999)

    @patch("app.controllers.customer_controller.db.session")
    def test_update_customer(self, mock_session):

        customer = SimpleNamespace(id=1, company="Company A", city="Seattle")

        customer_data = {"city": "Bengaluru"}

        result = customer_controller.update_customer(customer, customer_data)

        self.assertEqual(result.city, "Bengaluru")
        self.assertEqual(result.company, "Company A")

        mock_session.commit.assert_called_once()

    @patch("app.controllers.customer_controller.db.session")
    def test_update_customer_rollback_on_failure(self, mock_session):

        mock_session.commit.side_effect = Exception("Database error")

        customer = SimpleNamespace(id=1, company="Company A", city="Seattle")

        with self.assertRaises(Exception):
            customer_controller.update_customer(customer, {"city": "Bengaluru"})

        mock_session.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
