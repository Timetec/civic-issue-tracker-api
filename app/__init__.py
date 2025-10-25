from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .extensions import db, bcrypt, mail


# Load environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app) # Allow requests from your frontend
    bcrypt.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] =  ('Civic Issue Tracker', os.environ.get('MAIL_USERNAME'))


    mail.init_app(app)
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

    from .routes.issues import issues_bp
    app.register_blueprint(issues_bp, url_prefix='/api/issues')

    return app