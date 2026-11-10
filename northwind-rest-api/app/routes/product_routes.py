from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse

from app.controllers import product_controller

product_bp = Blueprint("products", __name__, url_prefix="/api/products")


@product_bp.route("", methods=["POST"])
def create_product():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = ProductCreate.model_validate(data)

        product = product_controller.create_product(validated_data.model_dump())

        response = ProductResponse.model_validate(product)

        return jsonify(response.model_dump(mode="json")), 201

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to create product"}), 500


@product_bp.route("", methods=["GET"])
def get_all_products():

    products = product_controller.get_all_products()

    response = [
        ProductResponse.model_validate(product).model_dump(mode="json")
        for product in products
    ]

    return jsonify(response), 200


@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):

    product = product_controller.get_product_by_id(product_id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    response = ProductResponse.model_validate(product)

    return jsonify(response.model_dump(mode="json")), 200


@product_bp.route("/<int:product_id>", methods=["PATCH"])
def update_product(product_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        validated_data = ProductUpdate.model_validate(data)

        if not validated_data.model_fields_set:
            return jsonify({"error": "At least one field must be provided"}), 400

        product = product_controller.get_product_by_id(product_id)

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        updated_data = validated_data.model_dump(exclude_unset=True)

        product = product_controller.update_product(product, updated_data)

        response = ProductResponse.model_validate(product)

        return jsonify(response.model_dump(mode="json")), 200

    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    except Exception:
        return jsonify({"error": "Unable to update product"}), 500
