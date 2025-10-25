from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
import os

from ..models import User
from .extensions import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User with this email already exists."}), 409

    new_user = User(
        email=data['email'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        mobile_number=data['mobileNumber'],
        role='Citizen' # Default role
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()
    
    # Create a token
    token = jwt.encode({
        'user_id': str(new_user.id),
        'exp': datetime.utcnow() + timedelta(days=7)
    }, os.environ.get('SECRET_KEY'), algorithm="HS256")
    
    user_data = new_user.to_dict()

    return jsonify({"token": token, "user": user_data}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handles user login.
    Expects a JSON body with 'email' and 'password'.
    Returns a JWT token and user object on success.
    """
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    email = data.get('email').lower()
    password = data.get('password')

    # Find the user by their email address
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    try:
        # Create the JWT token
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), # Token expires in 1 day
            'iat': datetime.datetime.utcnow(),
            'sub': user.id # Subject of the token is the user ID
        }
        token = jwt.encode(
            payload,
            os.environ.get('SECRET_KEY'),
            algorithm='HS256'
        )

        # Prepare user data for the response (excluding the password hash)
        user_data = user.to_dict()

        # Return the token and user object as specified in the contract
        return jsonify({
            "token": token,
            "user": user_data
        }), 200

    except Exception as e:
        # Log the exception e
        return jsonify({"message": "An error occurred during login"}), 500