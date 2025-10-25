from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

    from . import routes
    app.register_blueprint(routes.bp)

    return app