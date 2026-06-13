from app import db
from datetime import datetime

# Many-to-many: ServiceTickets <-> Mechanics
service_ticket_mechanics = db.Table(
    "service_ticket_mechanics",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id"), primary_key=True),
)

# Many-to-many: ServiceTickets <-> Inventory parts
service_ticket_inventory = db.Table(
    "service_ticket_inventory",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey("inventory.id"), primary_key=True),
)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship("ServiceTicket", back_populates="customer")


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Float, nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary=service_ticket_mechanics,
        back_populates="mechanics",
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), nullable=False)
    service_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    customer = db.relationship("Customer", back_populates="service_tickets")

    mechanics = db.relationship(
        "Mechanic",
        secondary=service_ticket_mechanics,
        back_populates="service_tickets",
    )

    inventory_parts = db.relationship(
        "Inventory",
        secondary=service_ticket_inventory,
        back_populates="service_tickets",
    )


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary=service_ticket_inventory,
        back_populates="inventory_parts",
    )
