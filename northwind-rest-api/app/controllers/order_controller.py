from app.extensions import db
from app.models import Order


def create_order(order_data):

    order = Order(**order_data)

    try:
        db.session.add(order)
        db.session.commit()

        return order

    except Exception:
        db.session.rollback()
        raise


def get_all_orders():

    orders = db.session.execute(db.select(Order)).scalars().all()

    return orders


def get_order_by_id(order_id):

    order = db.session.get(Order, order_id)

    return order


def update_order(order, order_data):

    try:
        for field, value in order_data.items():
            setattr(order, field, value)

        db.session.commit()

        return order

    except Exception:
        db.session.rollback()
        raise


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
