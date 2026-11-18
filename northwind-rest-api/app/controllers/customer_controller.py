from app.extensions import db
from app.models import Customer
from app.controllers.base_controller import BaseController

customer_crud = BaseController(Customer, db)


def create_customer(customer_data):
    return customer_crud.create(customer_data)


def get_all_customers():
    return customer_crud.get_all()


def get_customer_by_id(customer_id):
    return customer_crud.get_by_id(customer_id)


def update_customer(customer, customer_data):
    return customer_crud.update(customer, customer_data)
