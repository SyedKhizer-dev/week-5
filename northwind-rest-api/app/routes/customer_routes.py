from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.customer_schema import CustomerCreate, CustomerUpdate, CustomerResponse

from app.controllers import customer_controller

customer_bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@customer_bp.route("", methods=["POST"])
def create_customer():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = CustomerCreate.model_validate(data)

        customer = customer_controller.create_customer(validated_data.model_dump())

        response = CustomerResponse.model_validate(customer)

        return jsonify(response.model_dump(mode="json")), 201

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to create customer"}), 500


@customer_bp.route("", methods=["GET"])
def get_all_customers():

    customers = customer_controller.get_all_customers()

    response = [
        CustomerResponse.model_validate(customer).model_dump(mode="json")
        for customer in customers
    ]

    return jsonify(response), 200


@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):

    customer = customer_controller.get_customer_by_id(customer_id)

    if customer is None:
        return jsonify({"error": "Customer not found"}), 404

    response = CustomerResponse.model_validate(customer)

    return jsonify(response.model_dump(mode="json")), 200


@customer_bp.route("/<int:customer_id>", methods=["PATCH"])
def update_customer(customer_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = CustomerUpdate.model_validate(data)

        if not validated_data.model_fields_set:
            return jsonify({"error": "At least one field must be provided"}), 400

        customer = customer_controller.get_customer_by_id(customer_id)

        if customer is None:
            return jsonify({"error": "Customer not found"}), 404

        updated_data = validated_data.model_dump(exclude_unset=True)

        customer = customer_controller.update_customer(customer, updated_data)

        response = CustomerResponse.model_validate(customer)

        return jsonify(response.model_dump(mode="json")), 200

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to update customer"}), 500
