from flask import Flask
from app.config import Config
from app.extensions import db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app import models

    from app.routes.customer_routes import customer_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp, customer_order_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(customer_order_bp)

    return app
