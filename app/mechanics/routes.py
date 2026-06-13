from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app import db, cache
from app.models import Mechanic, service_ticket_mechanics
from app.mechanics.schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError

mechanics_bp = Blueprint("mechanics", __name__)


# ── POST /mechanics/ ── Create a new mechanic
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(data)
    db.session.commit()
    return mechanic_schema.jsonify(data), 201


# ── GET /mechanics/ ── Get all mechanics (cached for 60 seconds)
@mechanics_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_mechanics():
    all_mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(all_mechanics), 200


# ── GET /mechanics/<id> ── Get one mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["GET"])
def get_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    return mechanic_schema.jsonify(mechanic), 200


# ── PUT /mechanics/<id> ── Update a mechanic
@mechanics_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        updated = mechanic_schema.load(request.json, instance=mechanic)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return mechanic_schema.jsonify(updated), 200


# ── DELETE /mechanics/<id> ── Delete a mechanic
@mechanics_bp.route("/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted successfully"}), 200


# ── GET /mechanics/most-tickets ── Mechanics ordered by number of service tickets worked
@mechanics_bp.route("/most-tickets", methods=["GET"])
def most_tickets():
    results = (
        db.session.query(
            Mechanic,
            func.count(service_ticket_mechanics.c.service_ticket_id).label("ticket_count"),
        )
        .outerjoin(service_ticket_mechanics, Mechanic.id == service_ticket_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(service_ticket_mechanics.c.service_ticket_id).desc())
        .all()
    )

    data = []
    for mechanic, count in results:
        mechanic_data = mechanic_schema.dump(mechanic)
        mechanic_data["ticket_count"] = count
        data.append(mechanic_data)

    return jsonify(data), 200
