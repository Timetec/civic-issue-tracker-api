from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

from .models import db, User

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User with this email already exists."}), 409

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    new_user = User(
        email=data['email'],
        password_hash=hashed_password.decode('utf-8'),
        first_name=data['firstName'],
        last_name=data['lastName'],
        mobile_number=data['mobileNumber'],
        role='Citizen' # Default role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Create a token
    token = jwt.encode({
        'user_id': str(new_user.id),
        'exp': datetime.utcnow() + timedelta(days=7)
    }, os.environ.get('SECRET_KEY'), algorithm="HS256")
    
    user_data = {
        "email": new_user.email,
        "firstName": new_user.first_name,
        "lastName": new_user.last_name,
        "mobileNumber": new_user.mobile_number,
        "role": new_user.role
    }

    return jsonify({"token": token, "user": user_data}), 201

# ... Add other routes for login, issues, etc. here ...