from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..models import Issue, UserRole, User, Comment, IssueStatus
from ..utils.decorators import role_required, token_required
from sqlalchemy import or_, text
import google.generativeai as genai
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, timezone
import os
import json
import uuid
from functools import wraps
import requests
from ..extensions import db
import vercel_blob

# --- Flask Blueprint Definition ---


# --- Blueprint Definition ---
issues_bp = Blueprint('issues_bp', __name__)

# This would be your real Gemini client initialization

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

def upload_files_to_storage(files):
    """
    Upload files to Vercel Blob Storage and return their public URLs.
    """
    if not files or not files[0].filename:
        return ["/assets/placeholder-image.svg"]

    uploaded_urls = []

    for file in files:
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        file.seek(0)

        response = vercel_blob.put(filename, file_bytes, {
                "addRandomSuffix": "true",
            })

        uploaded_urls.append(response["url"])  # This is the public file URL

    return uploaded_urls

def categorize_issue_with_gemini(description: str, image_parts: list) -> dict:
    """Placeholder for calling the Gemini API to get a title and category."""
    print("Simulating Gemini API call...")
    try:
        prompt = f"""
            Analyze the user's report about a civic issue. Based on the description and any images,
            categorize it into one of: Pothole, Garbage, Streetlight, Graffiti, Flooding, Damaged Signage, Other.
            Also, create a concise, descriptive title for the report.

            User Description: "{description}"
            
            Return ONLY a valid JSON object with 'category' and 'title' keys.
            """
        contents = image_parts + [prompt]
        response = gemini_model.generate_content(contents)
        result = json.loads(response.text)
        # Add validation for category and title here
        return result
    except Exception as e:
        print(f"Gemini call failed: {e}")
        return {"category": "Other", "title": "Issue Report"}
    
def find_nearest_worker(location):
    """Find the nearest worker using PostGIS ST_Distance."""
    lat, lng = location

    # Use raw SQL for PostGIS geospatial query
    sql = text("""
        SELECT id, first_name as firstName, last_name as lastName, role, latitude, longitude,
               ST_Distance(
                   geography(ST_MakePoint(:lng, :lat)),
                   geography(ST_MakePoint(longitude, latitude))
               ) AS distance
        FROM users
        WHERE role = 'Worker'
        ORDER BY distance ASC
        LIMIT 1;
    """)

    result = db.session.execute(sql, {"lat": lat, "lng": lng}).fetchone()
    return dict(result) if result else None

# --- Flask Blueprint Definition ---

@issues_bp.route('/', methods=['POST'])
@token_required
def create_issue(current_user):
    """
    Creates a new civic issue.
    Receives multipart/form-data with description, location (JSON string), and photos.
    """
    try:
        print(f"Post issues api is triggered")
        # 1. Parse form data
        description = request.form.get('description')
        location_str = request.form.get('location')
        photos = request.files.getlist('photos')

        if not description or not location_str:
            return jsonify({"message": "Description and location are required."}), 400

        try:
            location = json.loads(location_str)
        except json.JSONDecodeError:
            return jsonify({"message": "Invalid location format. Must be valid JSON."}), 400

        # 2. Handle file uploads and prepare for Gemini
        photo_urls = upload_files_to_storage(photos)
        
        # Convert photos to Gemini-compatible 'Part' objects if they exist
        image_parts = []
        # for photo in photos:
        #    image_parts.append(Part.from_data(
        #        mime_type=photo.content_type,
        #        data=photo.read()
        #    ))
        #    photo.seek(0) # Reset file pointer after reading

        # 3. Call Gemini for AI-powered categorization and title
        ai_result = categorize_issue_with_gemini(description, image_parts)

        # 4. Find the nearest worker for automatic assignment
        assigned_worker = find_nearest_worker(location)

        # 5. Create the issue in the database (example using a dictionary)
        reporter = current_user.user
        new_issue_data = {
            "id": str(uuid.uuid4())[:8],
            "title": ai_result.get("title", "Issue Report"),
            "description": description,
            "category": ai_result.get("category", "Other"),
            "photoUrls": photo_urls,
            "location": location,
            "status": "Pending",
            "createdAt": datetime.now(timezone.utc),
            "reporterId": reporter['email'],
            "reporterName": f"{reporter['firstName']} {reporter['lastName']}",
            "assignedTo": assigned_worker['email'] if assigned_worker else None,
            "assignedToName": f"{assigned_worker['firstName']} {assigned_worker['lastName']}" if assigned_worker else None,
            "comments": []
        }
        
        # Using SQLAlchemy:
        new_issue = Issue(**new_issue_data)
        db.session.add(new_issue)
        db.session.commit()
        return jsonify(new_issue.to_dict()), 201

    except Exception as e:
        print(f"Error creating issue: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@issues_bp.route('/<string:issue_id>/comments/', methods=['POST'])
@token_required
def add_comment_to_issue(issue_id, current_user):
    """
    Adds a comment to a specific issue.
    Receives JSON with a 'text' field.
    """
    try:
        data = request.get_json()
        comment_text = data.get('text')

        if not comment_text:
            return jsonify({"message": "Comment text is required."}), 400

        # 1. Find the issue in the database
        issue = Issue.query.options(joinedload(Issue.comments)).get(issue_id)
        if not issue:
            return jsonify({"message": "Issue not found."}), 404
        
        # 2. Check if user is authorized to comment (example logic)
        author = current_user.user
        is_reporter = issue.reporterId == author.email
        is_assigned = issue.assignedTo == author.email
        is_admin = author.role == 'Admin'
        if not (is_reporter or is_assigned or is_admin):
            return jsonify({"message": "You are not authorized to comment on this issue."}), 403

        # 3. Create and add the new comment
        new_comment_data = {
            "id": str(uuid.uuid4()),
            "authorId": author['email'],
            "authorName": f"{author['firstName']} {author['lastName']}",
            "text": comment_text,
            "createdAt": datetime.now(timezone.utc),
        }
        
        # Using SQLAlchemy:
        new_comment = Comment(**new_comment_data)
        issue.comments.append(new_comment)
        db.session.commit()
        return jsonify(issue.to_dict()), 200

    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({"message": "An internal error occurred."}), 500
    
@issues_bp.route('/<string:issue_id>/status/', methods=['PUT'])
@role_required(UserRole.Admin) 
def update_issue_status(issue_id, current_user):
    """
    Updates the status of an issue.
    Accessible by Admins or the assigned Worker.
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({"message": "Status is required."}), 400
        
        # 1. Fetch the issue from the database
        issue = Issue.query.get(issue_id)
        if not issue:
            return jsonify({"message": "Issue not found."}), 404
        
        # 2. Authorization Check
        # In a real app `g.user` would be the SQLAlchemy object.
        is_admin = current_user.user['role'] == 'Admin'
        is_assigned_worker = current_user.user['email'] == issue['assignedTo']
        
        if not (is_admin or is_assigned_worker):
            # Simulate a worker trying to access an unassigned issue
            if current_user.user['role'] == 'Worker' and not is_assigned_worker:
                 print(f"Auth failed: Worker {current_user.user['email']} is not assigned to issue for {issue['assignedTo']}")
            return jsonify({"message": "You are not authorized to update this issue's status."}), 403

        # 3. Update the status and commit
        print(f"Updating issue {issue_id} status to '{new_status}'")
        issue.status = new_status
        db.session.commit()
        return jsonify(issue.to_dict()), 200
        
    except Exception as e:
        print(f"Error updating issue status: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@issues_bp.route('/<string:issue_id>/assign/', methods=['PUT'])
@role_required(UserRole.Admin)
def assign_issue_to_worker(issue_id):
    """
    Assigns an issue to a specific worker.
    Accessible by Admins only.
    """
    try:
        data = request.get_json()
        worker_email = data.get('workerEmail')
        
        if not worker_email:
            return jsonify({"message": "workerEmail is required."}), 400
            
        # 2. Fetch the issue and the worker from the database
        issue = Issue.query.get(issue_id)
        if not issue:
            return jsonify({"message": "Issue not found."}), 404
            
        worker = User.query.filter_by(email=worker_email, role='Worker').first()
        if not worker:
            return jsonify({"message": "Worker not found or user is not a worker."}), 404
        
        # 3. Update the issue and commit
        issue.assignedTo = worker.email
        issue.assignedToName = f"{worker.firstName} {worker.lastName}"
        db.session.commit()
        return jsonify(issue.to_dict()), 200
        
    except Exception as e:
        print(f"Error assigning issue: {e}")
        return jsonify({"message": "An internal error occurred."}), 500


@issues_bp.route('/<string:issue_id>/resolve/', methods=['PUT'])
@role_required(UserRole.Citizen)
def resolve_issue(issue_id, current_user):
    """
    Allows the original reporter to confirm an issue's resolution and provide a rating.
    Accessible only by the citizen who reported the issue.
    """
    try:
        data = request.get_json()
        rating = data.get('rating')

        if rating is None or not (1 <= rating <= 5):
            return jsonify({"message": "A rating between 1 and 5 is required."}), 400

        # 1. Fetch the issue from the database
        issue = Issue.query.get(issue_id)
        if not issue:
            return jsonify({"message": "Issue not found."}), 404
        
        # 2. Authorization Check
        if current_user.user['role'] != 'Citizen' or current_user.user['email'] != issue['reporterId']:
            return jsonify({"message": "You are not authorized to resolve this issue."}), 403

        # 3. Business Logic Check: Can only resolve if status is 'For Review'
        if issue.status != IssueStatus.ForReview:
            return jsonify({"message": f"Issue cannot be resolved with status '{issue.status}'."}), 409 # 409 Conflict
        
        # 4. Update the issue status and rating, then commit
        issue.status = IssueStatus.Resolved
        issue.rating = rating
        issue.resolvedAt = datetime.now(timezone.utc) # Optional: track resolution time
        db.session.commit()
        return jsonify(issue.to_dict()), 200

    except Exception as e:
        print(f"Error resolving issue: {e}")
        return jsonify({"message": "An internal error occurred."}), 500

@issues_bp.route('/', methods=['GET'])
@token_required
@role_required(UserRole.Admin)
def get_all_issues(current_user):
    """
    [Admin only] Retrieves all issues in the system.
    """
    try:
        issues = Issue.query.order_by(Issue.created_at.desc()).all()
        return jsonify([issue.to_dict() for issue in issues]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching issues"}), 500
    
@issues_bp.route('/reported/', methods=['GET'])
@token_required
@role_required(UserRole.Citizen)
def get_reported_issues(current_user):
    """
    [Citizen only] Returns issues reported by the authenticated citizen.
    """
    try:
        issues = Issue.query.filter_by(reporter_id=current_user.id).order_by(Issue.created_at.desc()).all()
        return jsonify([issue.to_dict() for issue in issues]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching reported issues"}), 500

@issues_bp.route('/assigned/', methods=['GET'])
@token_required
@role_required(UserRole.Worker)
def get_assigned_issues(current_user):
    """
    [Worker only] Returns issues assigned to the authenticated worker.
    """
    try:
        issues = Issue.query.filter_by(assigned_to_id=current_user.id).order_by(Issue.created_at.desc()).all()
        return jsonify([issue.to_dict() for issue in issues]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching assigned issues"}), 500
    
@issues_bp.route('/user/<string:identifier>/', methods=['GET'])
@token_required
@role_required(UserRole.Service)
def get_issues_by_user_identifier(current_user, identifier):
    """
    [Service role only] Returns issues for a specific user by email or mobile.
    """
    try:
        # Find the user by either email or mobile number
        target_user = User.query.filter(
            or_(User.email == identifier.lower(), User.mobile_number == identifier)
        ).first()

        if not target_user:
            # Return an empty list if the user doesn't exist, as per the contract
            return jsonify([]), 200

        # Fetch issues reported by that user
        issues = Issue.query.filter_by(reporter_id=target_user.id).order_by(Issue.created_at.desc()).all()
        return jsonify([issue.to_dict() for issue in issues]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while searching for user issues"}), 500


@issues_bp.route('/<string:id>/', methods=['GET'])
@token_required
def get_issue_by_id(current_user, id):
    """
    [Authenticated users] Returns a specific issue by its public ID,
    with role-based access checks.
    """
    try:
        issue = Issue.query.filter_by(public_id=id).first()

        if not issue:
            return jsonify({"message": "Issue not found"}), 404

        # Authorization check
        is_admin_or_service = current_user.role in [UserRole.Admin, UserRole.Service]
        is_reporter = current_user.id == issue.reporter_id
        is_assigned_worker = current_user.id == issue.assigned_to_id

        if not (is_admin_or_service or is_reporter or is_assigned_worker):
            return jsonify({"message": "Access forbidden: You are not authorized to view this issue."}), 403

        return jsonify(issue.to_dict()), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching the issue"}), 500
    

@issues_bp.route('/public/recent/', methods=['GET'])
def get_recent_public_issues():
    """
    Fetches all civic issues that were reported within the last 7 days.
    This is a public endpoint and does not require any authentication.
    """
    try:
        # Calculate the date and time for 7 days ago from the current UTC time.
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        recent_issues = Issue.query.filter(
            Issue.createdAt >= seven_days_ago
        ).order_by(Issue.createdAt.desc()).all()
        
        issues_list = [issue.to_dict() for issue in recent_issues]
        
        return jsonify(issues_list), 200

    except Exception as e:
        # It's important to log the actual error for debugging.
        print(f"Error fetching recent public issues: {e}")
        return jsonify({"message": "An error occurred while fetching recent issues."}), 500
    
