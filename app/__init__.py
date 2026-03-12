import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from pathlib import Path

from .extensions import db, migrate, jwt, bcrypt, mail


def create_app():

    # -------------------------
    # Load .env first
    # -------------------------
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / ".env")

    app = Flask(__name__)

    # -------------------------
    # Core configs
    # -------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # -------------------------
    # DATABASE CONFIG
    # -------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------------
    # MAIL CONFIG
    # -------------------------
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

    # -------------------------
    # Enable CORS for Angular
    # -------------------------
    CORS(
        app,
        origins=["http://localhost:4200"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # -------------------------
    # Initialize extensions
    # -------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # -------------------------
    # Register blueprints
    # -------------------------

    # Auth routes
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Ledger routes
    from .ledger.routes import ledger_bp
    app.register_blueprint(ledger_bp, url_prefix="/ledger")

    # Invoice routes
    from .invoices.routes import invoice_bp
    app.register_blueprint(invoice_bp, url_prefix="/invoice")

    # Load models
    from . import models

    return app