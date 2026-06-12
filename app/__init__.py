from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize extensions (not tied to any app yet)
db = SQLAlchemy()
ma = Marshmallow()


def create_app():
    app = Flask(__name__)

    # ---------------------------------------------------------------
    # DATABASE CONFIG
    # Replace <YOUR MYSQL PASSWORD> with your actual MySQL password
    # Example: if your password is "root123", write:
    #   mysql+mysqlconnector://root:root123@localhost/mechanic_shop_db
    # ---------------------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+mysqlconnector://root:Almomani123!@localhost/mechanic_shop_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind extensions to this app
    db.init_app(app)
    ma.init_app(app)

    # Register blueprints
    from app.customers.routes import customers_bp
    from app.mechanics.routes import mechanics_bp
    from app.service_tickets.routes import service_tickets_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")

    # Create all database tables on startup
    with app.app_context():
        db.create_all()

    return app
