from functools import wraps
from flask import request, jsonify, current_app
import jwt
from ..models import User, UserRole # Assuming your User model is in app/models.py

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for token in the 'Authorization' header
        if 'Authorization' in request.headers:
            # Expected format is "Bearer <token>"
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Malformed token. Use "Bearer <token>" format.'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the app's SECRET_KEY
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Find the user based on the 'sub' (subject) claim in the token
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'User not found.'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': 'An error occurred while decoding the token.'}), 500

        # Pass the authenticated user object to the decorated route function
        return f(current_user, *args, **kwargs)

    return decorated

def role_required(*roles: UserRole):
    """
    Decorator to ensure a user has a specific role.
    MUST be used *after* @token_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': 'Access forbidden: Insufficient permissions.'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator