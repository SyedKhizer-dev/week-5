from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.order_schema import OrderCreate, OrderUpdate, OrderResponse

from app.controllers import order_controller

order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

customer_order_bp = Blueprint("customer_orders", __name__, url_prefix="/api/customers")


@order_bp.route("", methods=["POST"])
def create_order():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = OrderCreate.model_validate(data)

        order = order_controller.create_order(validated_data.model_dump())

        response = OrderResponse.model_validate(order)

        return jsonify(response.model_dump(mode="json")), 201

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to create order"}), 500


@order_bp.route("", methods=["GET"])
def get_all_orders():

    orders = order_controller.get_all_orders()

    response = [
        OrderResponse.model_validate(order).model_dump(mode="json") for order in orders
    ]

    return jsonify(response), 200


@order_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):

    order = order_controller.get_order_by_id(order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    response = OrderResponse.model_validate(order)

    return jsonify(response.model_dump(mode="json")), 200


@order_bp.route("/<int:order_id>", methods=["PATCH"])
def update_order(order_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = OrderUpdate.model_validate(data)

        if not validated_data.model_fields_set:
            return jsonify({"error": "At least one field must be provided"}), 400

        order = order_controller.get_order_by_id(order_id)

        if order is None:
            return jsonify({"error": "Order not found"}), 404

        updated_data = validated_data.model_dump(exclude_unset=True)

        order = order_controller.update_order(order, updated_data)

        response = OrderResponse.model_validate(order)

        return jsonify(response.model_dump(mode="json")), 200

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to update order"}), 500


@customer_order_bp.route("/<int:customer_id>/orders", methods=["GET"])
def get_customer_order_history(customer_id):

    orders = order_controller.get_customer_order_history(customer_id)

    response = [
        OrderResponse.model_validate(order).model_dump(mode="json") for order in orders
    ]

    return jsonify(response), 200
