from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    # Security key
    app.config["SECRET_KEY"] = "secretkey123"

    # Database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pigpeople.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Where to redirect if not logged in
    login_manager.login_view = "login"

    # Register routes
    from .routes import register_routes
    register_routes(app)

    # ================= CURRENCY FILTER (ZMW) =================
    @app.template_filter('zmw')
    def format_zmw(value):
        try:
            return f"ZMW {float(value):,.2f}"
        except (ValueError, TypeError):
            return "ZMW 0.00"
    # ==========================================================

    return app