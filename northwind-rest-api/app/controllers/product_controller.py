from app.extensions import db
from app.models import Product


def create_product(product_data):

    product = Product(**product_data)

    try:
        db.session.add(product)
        db.session.commit()

        return product

    except Exception:
        db.session.rollback()
        raise


def get_all_products():

    products = db.session.execute(db.select(Product)).scalars().all()

    return products


def get_product_by_id(product_id):

    product = db.session.get(Product, product_id)

    return product


def update_product(product, product_data):

    try:
        for field, value in product_data.items():
            setattr(product, field, value)

        db.session.commit()

        return product

    except Exception:
        db.session.rollback()
        raise
