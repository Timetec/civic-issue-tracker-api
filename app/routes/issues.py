from flask import Blueprint, jsonify
from functools import wraps
from ..models import Issue, UserRole
from ..utils.decorators import role_required, token_required

# --- Blueprint Definition ---
issues_bp = Blueprint('issues_bp', __name__)

# --- API Route Implementation ---
@issues_bp.route('/', methods=['GET'])
@token_required
@role_required(UserRole.Admin)
def get_all_issues(current_user):
    """
    Retrieves all issues in the system.
    Accessible only by users with the 'Admin' role.
    The 'current_user' object is passed by the @token_required decorator.
    """
    try:
        # Query all issues from the database, ordering by most recent
        issues = Issue.query.order_by(Issue.created_at.desc()).all()

        # Serialize the list of issue objects into dictionaries
        # This assumes your Issue model has a .to_dict() method
        issues_list = [issue.to_dict() for issue in issues]

        return jsonify(issues_list), 200

    except Exception as e:
        # Log the error e for debugging
        return jsonify({"message": "An error occurred while fetching issues"}), 500