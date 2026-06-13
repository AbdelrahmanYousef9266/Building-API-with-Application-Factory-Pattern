from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models import Customer
from app.customers.schemas import customer_schema, customers_schema, login_schema
from app.utils import encode_token, token_required
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


# ── GET /customers/ ── Get all customers (rate limited: 5/min, paginated)
@customers_bp.route("/", methods=["GET"])
@limiter.limit("5 per minute")
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    paginated = Customer.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "customers": customers_schema.dump(paginated.items),
        "page": paginated.page,
        "per_page": paginated.per_page,
        "total": paginated.total,
        "pages": paginated.pages,
    }), 200


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


# ── POST /customers/login ── Customer login, returns JWT token
@customers_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = Customer.query.filter_by(email=data["email"]).first()

    if not customer or customer.password != data["password"]:
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token, "message": "Login successful"}), 200


# ── GET /customers/my-tickets ── Get tickets for the logged-in customer (JWT protected)
@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(customer_id):
    from app.service_tickets.schemas import service_tickets_schema

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return service_tickets_schema.jsonify(customer.service_tickets), 200
