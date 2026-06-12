from flask import Blueprint, request, jsonify
from app import db
from app.models import Customer
from app.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError

customers_bp = Blueprint("customers", __name__)


# ── POST /customers/ ── Create a new customer
@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(data)
    db.session.commit()
    return customer_schema.jsonify(data), 201


# ── GET /customers/ ── Get all customers
@customers_bp.route("/", methods=["GET"])
def get_customers():
    all_customers = Customer.query.all()
    return customers_schema.jsonify(all_customers), 200


# ── GET /customers/<id> ── Get one customer by ID
@customers_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return customer_schema.jsonify(customer), 200


# ── PUT /customers/<id> ── Update a customer
@customers_bp.route("/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        # partial=False means all fields in schema are expected (strict update)
        updated = customer_schema.load(request.json, instance=customer)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return customer_schema.jsonify(updated), 200


# ── DELETE /customers/<id> ── Delete a customer
@customers_bp.route("/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted successfully"}), 200
