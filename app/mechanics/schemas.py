from app import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True  # Deserialize directly into a Mechanic object


# Single mechanic
mechanic_schema = MechanicSchema()

# List of mechanics
mechanics_schema = MechanicSchema(many=True)
