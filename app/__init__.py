from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_cors import CORS
from dotenv import load_dotenv
import os

from .models import db

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app) # Allow requests from your frontend

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        try:
            print("🔄 Running database migrations...")
            upgrade()
            print("✅ Database is up to date.")
        except Exception as e:
            print(f"⚠️ Skipping migration due to error: {e}")

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from .routes.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')

    return app