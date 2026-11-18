from app.extensions import db
from app.models import Order
from app.controllers.base_controller import BaseController

order_crud = BaseController(Order, db)


def create_order(order_data):
    return order_crud.create(order_data)


def get_all_orders():
    return order_crud.get_all()


def get_order_by_id(order_id):
    return order_crud.get_by_id(order_id)


def update_order(order, order_data):
    return order_crud.update(order, order_data)


def get_customer_order_history(customer_id):

    orders = (
        db.session.execute(
            db.select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
        )
        .scalars()
        .all()
    )

    return orders
