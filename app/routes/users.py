from flask import Blueprint, request, jsonify
from ..utils.decorators import token_required, role_required
from ..models import User, UserRole
from ..extensions import db

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/', methods=['GET'])
@token_required
@role_required(UserRole.Admin)
def get_all_users(current_user):
    """
    Retrieves a list of all users.
    Accessible only by users with the 'Admin' role.
    """
    try:
        users = User.query.all()
        users_list = [user.to_dict() for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching users"}), 500

@users_bp.route('/', methods=['POST'])
@token_required
@role_required(UserRole.Admin)
def create_user(current_user):
    """
    Creates a new user (Worker or Service).
    Accessible only by users with the 'Admin' role.
    """
    data = request.get_json()
    required_fields = ['email', 'password', 'firstName', 'lastName', 'mobileNumber', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    email = data['email'].lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists"}), 409

    try:
        role = UserRole[data['role']]
        if role not in [UserRole.Worker, UserRole.Service]:
            return jsonify({"message": "Can only create users with Worker or Service role"}), 400
    except KeyError:
        return jsonify({"message": "Invalid role specified"}), 400

    new_user = User(
        email=email,
        first_name=data['firstName'],
        last_name=data['lastName'],
        mobile_number=data['mobileNumber'],
        role=role
    )
    new_user.set_password(data['password'])

    if 'location' in data and data['location'] and role == UserRole.Worker:
        new_user.location_lat = data['location'].get('lat')
        new_user.location_lng = data['location'].get('lng')

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create user due to a database error"}), 500



@users_bp.route('/me/', methods=['GET'])
@token_required
def get_me(current_user: User):
    """
    Gets the currently authenticated user's profile.
    The 'current_user' object is passed by the @token_required decorator.
    """
    if not current_user:
        # This is a safeguard, though the decorator should prevent this
        return jsonify({"message": "User not found or authentication failed"}), 404

    try:

        return jsonify(current_user.to_dict()), 200
    
    except Exception as e:
        # Log the exception e
        return jsonify({"message": "An error occurred while fetching user data"}), 500
    
@users_bp.route('/me/', methods=['PUT'])
@token_required
def update_me(current_user):
    """
    Updates the currently authenticated user's profile.
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body is empty"}), 400

    current_user.first_name = data.get('firstName', current_user.first_name)
    current_user.last_name = data.get('lastName', current_user.last_name)
    current_user.mobile_number = data.get('mobileNumber', current_user.mobile_number)

    try:
        db.session.commit()
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update profile"}), 500
    
@users_bp.route('/me/password/', methods=['PUT'])
@token_required
def update_my_password(current_user):
    """
    Updates the currently authenticated user's password.
    """
    data = request.get_json()
    if not data or 'oldPassword' not in data or 'newPassword' not in data:
        return jsonify({"message": "oldPassword and newPassword are required"}), 400

    if not current_user.check_password(data['oldPassword']):
        return jsonify({"message": "Incorrect old password"}), 401
    
    current_user.set_password(data['newPassword'])
    try:
        db.session.commit()
        # Per the contract, just return a 200 OK status with no body.
        return "", 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update password"}), 500

@users_bp.route('/me/location/', methods=['PUT'])
@token_required
def update_my_location(current_user):
    """
    Updates the currently authenticated user's location (primarily for Workers).
    """
    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"message": "lat and lng are required"}), 400

    current_user.location_lat = data['lat']
    current_user.location_lng = data['lng']

    try:
        db.session.commit()
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update location"}), 500