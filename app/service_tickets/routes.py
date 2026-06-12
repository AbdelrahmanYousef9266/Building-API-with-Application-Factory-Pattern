from flask import Blueprint, request, jsonify
from app import db
from app.models import ServiceTicket, Mechanic
from app.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from marshmallow import ValidationError

service_tickets_bp = Blueprint("service_tickets", __name__)


# ── POST /service-tickets/ ── Create a new service ticket
@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(data)
    db.session.commit()
    return service_ticket_schema.jsonify(data), 201


# ── GET /service-tickets/ ── Get all service tickets
@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    all_tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(all_tickets), 200


# ── PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>
# Assign a mechanic to a service ticket
@service_tickets_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Prevent duplicate assignment
    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic is already assigned to this ticket"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return jsonify({
        "message": f"Mechanic {mechanic.name} assigned to ticket {ticket_id}"
    }), 200


# ── PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>
# Remove a mechanic from a service ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic is not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify({
        "message": f"Mechanic {mechanic.name} removed from ticket {ticket_id}"
    }), 200
