# from flask import render_template
# from flask_mail import Message
# from threading import Thread
# from .extensions import mail
# # Import your app instance and mail instance from your main file
# # You might need to adjust this import based on your project structure
# from app import app 

# def send_async_email(app_context, msg):
#     """
#     Sends an email in a background thread to avoid blocking the main application.
#     """
#     with app_context:
#         try:
#             mail.send(msg)
#         except Exception as e:
#             # In a real application, you should use a proper logger here
#             print(f"Failed to send email: {e}")

# def send_email(subject, recipients, html_body):
#     """
#     Creates an email message and starts the background thread to send it.
    
#     :param subject: The subject line of the email.
#     :param recipients: A list of recipient email addresses.
#     :param html_body: The HTML content of the email.
#     """
#     msg = Message(subject, recipients=recipients)
#     msg.html = html_body
#     # Run the email sending in a background thread
#     thread = Thread(target=send_async_email, args=(app.app_context(), msg))
#     thread.start()

# # --- Notification Functions ---

# def send_new_issue_notification(user, issue):
#     """
#     Renders and sends the simple confirmation email for a new issue.
    
#     :param user: The user object (dict or class) who reported the issue. 
#                  Must have 'firstName' and 'email'.
#     :param issue: The issue object (dict or class). 
#                   Must have 'id' and 'status'.
#     """
#     subject = f"Confirmation: Your Issue Report #{issue['public_id']} Has Been Received"
    
#     # Render the simple HTML template with the provided data
#     html_body = render_template(
#         'new_issue_template.html', 
#         user=user, 
#         issue=issue
#     )
    
#     send_email(subject, [user['email']], html_body)


# def send_status_update_notification(user, issue, new_status):
#     """
#     Renders and sends the simple notification email for an issue status change.
    
#     :param user: The user object of the reporter. Must have 'firstName' and 'email'.
#     :param issue: The issue object. Must have 'id'.
#     :param new_status: The new status string (e.g., 'In Progress').
#     """
#     subject = f"Update: Status of Your Issue #{issue['id']} is now '{new_status}'"
    
#     html_body = render_template(
#         'status_update_template.html',
#         user=user,
#         issue=issue,
#         new_status=new_status
#     )
    
#     send_email(subject, [user['email']], html_body)