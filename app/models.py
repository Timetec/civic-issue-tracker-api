from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='Citizen')
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)

class Issue(db.Model):
    id = db.Column(db.String(10), primary_key=True) # Short, random ID
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    photo_urls = db.Column(db.JSON) # Store a list of photo URLs
    location_lat = db.Column(db.Float, nullable=False)
    location_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer)

    reporter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    reporter = db.relationship('User', foreign_keys=[reporter_id])

    assigned_to_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])