from app import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
import datetime
db = SQLAlchemy()

# Define Enums for roles and statuses to match the frontend
class UserRole(enum.Enum):
    Citizen = 'Citizen'
    Worker = 'Worker'
    Admin = 'Admin'
    Service = 'Service'

class IssueStatus(enum.Enum):
    Pending = 'Pending'
    InProgress = 'In Progress'
    ForReview = 'For Review'
    Resolved = 'Resolved'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_id = db.Column(db.String(8), db.ForeignKey('issues.public_id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'createdAt': self.created_at.isoformat() + 'Z',
            'authorId': self.author.email,
            'authorName': f"{self.author.first_name} {self.author.last_name}"
        }

class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    # Using a shorter, unique string for the public-facing ID
    public_id = db.Column(db.String(8), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    photo_urls = db.Column(db.JSON, nullable=True) # Storing a list of photo URLs
    location_lat = db.Column(db.Float, nullable=False)
    location_lng = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(IssueStatus), nullable=False, default=IssueStatus.Pending)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    
    # Relationships
    comments = db.relationship('Comment', backref='issue', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        """Serializes the Issue object to a dictionary."""
        return {
            'id': self.public_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'photoUrls': self.photo_urls or [],
            'location': {
                'lat': self.location_lat,
                'lng': self.location_lng
            },
            'status': self.status.value,
            'createdAt': self.created_at.isoformat() + 'Z',
            'reporterId': self.reporter.email,
            'reporterName': f"{self.reporter.first_name} {self.reporter.last_name}",
            'assignedTo': self.assigned_worker.email if self.assigned_worker else None,
            'assignedToName': f"{self.assigned_worker.first_name} {self.assigned_worker.last_name}" if self.assigned_worker else None,
            'comments': [comment.to_dict() for comment in self.comments],
            'rating': self.rating
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.Citizen)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    
    # Relationships
    reported_issues = db.relationship('Issue', foreign_keys='Issue.reporter_id', backref='reporter', lazy='dynamic')
    assigned_issues = db.relationship('Issue', foreign_keys='Issue.assigned_to_id', backref='assigned_worker', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serializes the User object to a dictionary, omitting the password."""
        return {
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'mobileNumber': self.mobile_number,
            'role': self.role.value,
            'location': {
                'lat': self.location_lat,
                'lng': self.location_lng
            } if self.location_lat is not None and self.location_lng is not None else None
        }