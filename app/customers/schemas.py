from app import ma
from app.models import Customer
from marshmallow_sqlalchemy import auto_field


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True  # Deserialize directly into a Customer object


# Single customer (used for GET by id, POST, PUT)
customer_schema = CustomerSchema()

# List of customers (used for GET all)
customers_schema = CustomerSchema(many=True)
