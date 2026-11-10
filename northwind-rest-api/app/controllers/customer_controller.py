from app.extensions import db
from app.models import Customer


def create_customer(customer_data):

    customer = Customer(**customer_data)

    try:
        db.session.add(customer)
        db.session.commit()

        return customer

    except Exception:
        db.session.rollback()
        raise


def get_all_customers():

    customers = db.session.execute(db.select(Customer)).scalars().all()

    return customers


def get_customer_by_id(customer_id):

    customer = db.session.get(Customer, customer_id)

    return customer


def update_customer(customer, customer_data):

    try:
        for field, value in customer_data.items():
            setattr(customer, field, value)

        db.session.commit()

        return customer

    except Exception:
        db.session.rollback()
        raise
