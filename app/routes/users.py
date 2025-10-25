from flask import Blueprint, jsonify
from ..utils.decorators import token_required 
from ..models import User 

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/me', methods=['GET'])
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
        # Prepare user data for the response, excluding the password hash
        user_data = {
            'email': current_user.email,
            'firstName': current_user.first_name,
            'lastName': current_user.last_name,
            'mobileNumber': current_user.mobile_number,
            'role': current_user.role.value, # Assuming UserRole is an Enum
            'location': {
                'lat': current_user.location_lat,
                'lng': current_user.location_lng
            } if current_user.location_lat is not None else None
        }

        # Return the user object as specified in the contract
        return jsonify(user_data), 200

    except Exception as e:
        # Log the exception e
        return jsonify({"message": "An error occurred while fetching user data"}), 500