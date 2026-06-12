from app import ma
from app.models import ServiceTicket
from marshmallow_sqlalchemy import auto_field
import marshmallow as m


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True  # Include customer_id foreign key in serialization


# Single service ticket
service_ticket_schema = ServiceTicketSchema()

# List of service tickets
service_tickets_schema = ServiceTicketSchema(many=True)
