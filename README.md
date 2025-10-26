
# CivicVoice - Backend API (Python/Flask)

![CivicVoice Hero Image](./public/assets/hero-image.svg)

This repository contains the backend API for the **CivicVoice** application. It is a robust, scalable, and secure RESTful API built with Python and the Flask framework. It handles all business logic, data persistence, and integration with third-party services like Google Gemini, leaving the frontend free to focus on the user experience.

The API is designed for serverless deployment on **Vercel**, using **Neon** for the PostgreSQL database and **Vercel Blob** for cloud-based image storage.

---

## ✨ Key Backend Features

*   **Secure Authentication**: Implements JSON Web Token (JWT) based authentication for secure user sessions and protected endpoints.
*   **Role-Based Access Control (RBAC)**: Enforces strict permissions, ensuring that users can only access data and perform actions appropriate for their role (Citizen, Worker, Admin, Service).
*   **Full CRUD Operations**: Provides a complete set of endpoints for managing users, civic issues, and comments.
*   **AI-Powered Issue Processing**:
    *   On new issue submission, the backend receives the description and uploaded photos.
    *   It securely calls the **Google Gemini API** to analyze the content, automatically generating a concise title and assigning an appropriate category.
*   **Geolocation-Based Worker Assignment**:
    *   When a new issue is created, the system queries the database for all 'Worker' users with a registered location.
    *   It calculates the distance to each worker and automatically assigns the issue to the one who is closest, streamlining dispatch.
*   **Cloud Image Storage**:
    *   Accepts multipart/form-data for image uploads.
    *   Securely uploads and stores images in **Vercel Blob**, returning a publicly accessible URL for the frontend to display.
*   **Database Management**: Uses SQLAlchemy ORM for database interactions and Flask-Migrate for handling schema migrations, making database management simple and version-controlled.

---

## 🛠️ Technology Stack

*   **Backend Framework**: [Python 3.11+](https://www.python.org/), [Flask](https://flask.palletsprojects.com/)
*   **Database**: [Neon](https://neon.tech/) (Serverless PostgreSQL)
*   **Object-Relational Mapper (ORM)**: [SQLAlchemy](https://www.sqlalchemy.org/)
*   **Database Migrations**: [Flask-Migrate](https://flask-migrate.readthedocs.io/) (using Alembic)
*   **Authentication**: [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
*   **Deployment**: [Vercel Serverless Functions](https://vercel.com/docs/functions/serverless-functions)
*   **File Storage**: [Vercel Blob](https://vercel.com/storage/blob)
*   **Generative AI**: [Google Gemini API](https://ai.google.dev/)
*   **CORS Handling**: [Flask-Cors](https://flask-cors.readthedocs.io/)

---

## 🚀 Getting Started Locally

Follow these instructions to get the backend server up and running on your local machine for development.

### Prerequisites

*   Python 3.11 or newer
*   `pip` and `venv` (usually included with Python)
*   A Neon account (for the database)
*   A Google AI Studio account (for the Gemini API key)
*   A Vercel account (for Blob storage token)

### Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/civicvoice-backend.git
    cd civicvoice-backend
    ```

2.  **Create and Activate a Virtual Environment**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    py -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root of the project. This file is ignored by Git and will store your secret keys.

    *   Create the file:
        ```sh
        touch .env
        ```
    *   Add the following content, replacing the placeholders with your actual keys:

        ```env
        # --- Flask Configuration ---
        FLASK_APP=app.py
        FLASK_ENV=development
        # Generate a secure secret key. You can use: python -c 'import secrets; print(secrets.token_hex())'
        JWT_SECRET_KEY=your_super_secret_jwt_key

        # --- Database (Neon) ---
        # Get this from your Neon project dashboard (it's the PSQL connection string)
        DATABASE_URL="postgresql://user:password@host:port/dbname?sslmode=require"

        # --- Google Gemini API ---
        # Get this from Google AI Studio
        GEMINI_API_KEY=your_gemini_api_key

        # --- Vercel Blob Storage ---
        # Create a Blob store in your Vercel project and get the read-write token
        BLOB_READ_WRITE_TOKEN=your_vercel_blob_read_write_token
        ```

5.  **Set Up the Database**
    Run the following commands to initialize the database schema using Flask-Migrate.
    ```sh
    flask db init  # Only run this the very first time
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
    Your Neon database is now ready and its schema matches your models.

6.  **Run the Application**
    Start the local development server:
    ```sh
    flask run
    ```
    The API will be available at `http://127.0.0.1:5000`. You can now connect your frontend application to this URL by setting `VITE_API_BASE_URL=http://127.0.0.1:5000` in the frontend's `.env` file.

---

## 🔌 API Contract

The API adheres to the following RESTful contract. All endpoints are prefixed with `/api`.

#### Authentication (`/auth`)
*   `POST /auth/register`
*   `POST /auth/login`

#### Users (`/users`)
*   `GET /users` (Admin only)
*   `POST /users` (Admin only)
*   `GET /users/me` (Authenticated)
*   `PUT /users/me` (Authenticated)
*   `PUT /users/me/password` (Authenticated)
*   `PUT /users/me/location` (Authenticated)

#### Issues (`/issues`)
*   `GET /issues` (Admin only)
*   `GET /issues/reported` (Citizen only)
*   `GET /issues/assigned` (Worker only)
*   `GET /issues/public/recent` (Public, for map view)
*   `GET /issues/user/<identifier>` (Service role only)
*   `GET /issues/<id>` (Authenticated, with role-based checks)
*   `POST /issues` (Authenticated)
*   `POST /issues/<id>/comments` (Authorized)
*   `PUT /issues/<id>/status` (Admin/Worker)
*   `PUT /issues/<id>/assign` (Admin only)
*   `PUT /issues/<id>/resolve` (Citizen reporter only)

---

## 🌐 Deployment to Vercel

This project is configured for seamless deployment to Vercel as a serverless Python function.

1.  **Push to a Git Repository**: Make sure your code is pushed to a GitHub, GitLab, or Bitbucket repository.

2.  **Create a Vercel Project**:
    *   On your Vercel dashboard, click "Add New... -> Project".
    *   Import your Git repository.
    *   Vercel will automatically detect that it's a Python project using Flask. No framework preset is needed.

3.  **Configure Environment Variables**:
    *   In your Vercel project's settings, go to the "Environment Variables" section.
    *   Add all the variables from your local `.env` file (`JWT_SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`, `BLOB_READ_WRITE_TOKEN`).
    *   **Important**: Ensure `FLASK_ENV` is set to `production`.

4.  **Configure `vercel.json`**: A `vercel.json` file in the root of your project tells Vercel how to handle routing and build the project. A typical configuration looks like this:
    ```json
    {
      "builds": [
        {
          "src": "app.py",
          "use": "@vercel/python"
        }
      ],
      "routes": [
        {
          "src": "/(.*)",
          "dest": "app.py"
        }
      ]
    }
    ```

5.  **Deploy**: Trigger a deployment from the Vercel dashboard or by pushing a new commit to your main branch. Vercel will handle installing dependencies from `requirements.txt` and deploying the app.

6.  **Run Database Migrations**: After a successful deployment, you may need to run database migrations on your production database. You can do this by temporarily connecting your local machine to the production database URL and running `flask db upgrade`.

---

## 🔮 Future Improvements

*   **Email Notifications**: Implement a system to send email notifications to users upon status changes or new comments on their reported issues. The codebase includes commented-out placeholders where this logic can be integrated, likely using a service like SendGrid or AWS SES.
*   **WebSocket for Real-time Updates**: Integrate WebSockets to push live updates to the frontend, such as new comments or status changes, without requiring a page refresh.
*   **Advanced Analytics Dashboard**: Create an admin-only dashboard to visualize issue data, such as resolution times, common issue types, and worker performance metrics.
