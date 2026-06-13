from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize extensions (not tied to any app yet)
db = SQLAlchemy()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")
cache = Cache()


def create_app():
    app = Flask(__name__)

    # ---------------------------------------------------------------
    # DATABASE CONFIG
    # Replace the connection string below with your MySQL credentials
    # ---------------------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+mysqlconnector://root:Almomani123!@localhost/mechanic_shop_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Secret key used to sign JWT tokens
    app.config["SECRET_KEY"] = "mechanic-shop-secret-key-2024"

    # Flask-Caching — SimpleCache keeps everything in memory (great for development)
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60

    # Bind extensions to this app
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register blueprints
    from app.customers.routes import customers_bp
    from app.mechanics.routes import mechanics_bp
    from app.service_tickets.routes import service_tickets_bp
    from app.inventory.routes import inventory_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    # Create all database tables on startup
    with app.app_context():
        db.create_all()

    return app
