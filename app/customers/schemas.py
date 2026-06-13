from app import ma
from app.models import Customer
import marshmallow as m


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

    # load_only=True means password is accepted on input but NEVER returned in responses
    password = m.fields.String(load_only=True, required=True)


class LoginSchema(m.Schema):
    email = m.fields.Email(required=True)
    password = m.fields.String(required=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()
