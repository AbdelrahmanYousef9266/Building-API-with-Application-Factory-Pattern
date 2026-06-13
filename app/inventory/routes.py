from flask import Blueprint, request, jsonify
from app import db
from app.models import Inventory
from app.inventory.schemas import inventory_schema, inventories_schema
from marshmallow import ValidationError

inventory_bp = Blueprint("inventory", __name__)


# ── POST /inventory/ ── Create a new inventory part
@inventory_bp.route("/", methods=["POST"])
def create_inventory():
    try:
        data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(data)
    db.session.commit()
    return inventory_schema.jsonify(data), 201


# ── GET /inventory/ ── Get all inventory parts
@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    all_parts = Inventory.query.all()
    return inventories_schema.jsonify(all_parts), 200


# ── GET /inventory/<id> ── Get a single inventory part
@inventory_bp.route("/<int:id>", methods=["GET"])
def get_inventory_item(id):
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404
    return inventory_schema.jsonify(part), 200


# ── PUT /inventory/<id> ── Update an inventory part
@inventory_bp.route("/<int:id>", methods=["PUT"])
def update_inventory(id):
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        updated = inventory_schema.load(request.json, instance=part)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return inventory_schema.jsonify(updated), 200


# ── DELETE /inventory/<id> ── Delete an inventory part
@inventory_bp.route("/<int:id>", methods=["DELETE"])
def delete_inventory(id):
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Inventory item {id} deleted successfully"}), 200
