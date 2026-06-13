from app import ma
from app.models import ServiceTicket
import marshmallow as m


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True  # Include customer_id in serialization

    # Show IDs of assigned mechanics in the response
    mechanic_ids = m.fields.Method("get_mechanic_ids", dump_only=True)

    # Show IDs of added inventory parts in the response
    inventory_part_ids = m.fields.Method("get_inventory_part_ids", dump_only=True)

    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]

    def get_inventory_part_ids(self, obj):
        return [part.id for part in obj.inventory_parts]


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
