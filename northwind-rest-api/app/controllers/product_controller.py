from app.extensions import db
from app.models import Product
from app.controllers.base_controller import BaseController

product_crud = BaseController(Product, db)


def create_product(product_data):
    return product_crud.create(product_data)


def get_all_products():
    return product_crud.get_all()


def get_product_by_id(product_id):
    return product_crud.get_by_id(product_id)


def update_product(product, product_data):
    return product_crud.update(product, product_data)
