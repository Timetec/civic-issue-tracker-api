# Civic Issue Tracker - Backend API

This repository contains the Python/Flask backend API for the **Civic Issue Tracker** application. It provides a secure, scalable, and robust server-side solution to handle user authentication, issue management, and integration with third-party services like the Google Gemini API.

This backend is designed to be deployed as a serverless function on platforms like Vercel, ensuring high availability and cost-efficiency.

---

## 🛠️ Technology Stack

*   **Language**: Python 3.10+
*   **Framework**: Flask
*   **Database ORM**: Flask-SQLAlchemy
*   **Database Migrations**: Flask-Migrate
*   **Authentication**: JSON Web Tokens (JWT)
*   **AI Integration**: Google Gemini API (`gemini-2.5-flash`) for issue analysis.
*   **Database**: PostgreSQL (recommended for production), SQLite (for local development)
*   **WSGI Server**: Gunicorn
*   **Deployment**: Vercel Serverless Functions

---

## 🚀 Getting Started

Follow these instructions to get the backend server up and running on your local machine for development and testing.

### 1. Prerequisites

*   Python 3.10 or higher installed.
*   `pip` and `venv` for package management.

### 2. Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/civic-issue-tracker-backend.git
    cd civic-issue-tracker-backend
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
    A `requirements.txt` file should be in your project with all necessary packages.
    ```sh
    pip install -r requirements.txt
    ```

### 3. Configure Environment Variables

Create a `.env` file in the root of the project. This file is ignored by Git and will hold your secret keys.

*   Create the file:
    ```sh
    touch .env
    ```
*   Add the following content, replacing the placeholders:

    ```env
    # A long, random string used for signing JWTs and session data.
    # You can generate one using: python -c 'import secrets; print(secrets.token_hex())'
    SECRET_KEY=YOUR_SUPER_SECRET_KEY

    # Connection string for your database.
    # For local SQLite development:
    DATABASE_URL="sqlite:///dev.db"
    # For production PostgreSQL (e.g., from Vercel Postgres):
    # DATABASE_URL="postgres://user:password@host:port/dbname"

    # Your Google Gemini API Key for issue categorization.
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```

### 4. Set Up the Database

This project uses Flask-Migrate to handle database schema changes.

1.  **Initialize the migration environment** (only run this once):
    ```sh
    flask db init
    ```

2.  **Create an initial migration** based on the models in `app/models.py`:
    ```sh
    flask db migrate -m "Initial database schema"
    ```

3.  **Apply the migration** to create your database tables:
    ```sh
    flask db upgrade
    ```
    Whenever you change your database models, you will need to run the `migrate` and `upgrade` commands again.

### 5. Run the Application

Start the local Flask development server:
```sh
flask run
```
The API will now be running at `http://127.0.0.1:5000`. You can now point your frontend application's `VITE_API_BASE_URL` to this address.

---

## 🔌 API Contract

The server implements the following RESTful endpoints. Authentication is handled via Bearer Tokens (JWT) in the `Authorization` header.

#### Authentication (`/api/auth`)
*   `POST /api/auth/register`
    *   **Body**: `{ email, password, firstName, lastName, mobileNumber }`
    *   **Response (201)**: `{ token: "jwt_token", user: { ...userObject } }`
*   `POST /api/auth/login`
    *   **Body**: `{ email, password }`
    *   **Response (200)**: `{ token: "jwt_token", user: { ...userObject } }`

#### Users (`/api/users`)
*   `GET /api/users` (Admin only)
    *   **Response (200)**: `[ { ...userObject }, ... ]`
*   `POST /api/users` (Admin only)
    *   **Body**: `{ email, password, firstName, lastName, mobileNumber, role, location? }`
    *   **Response (201)**: `{ ...userObject }`
*   `GET /api/users/me` (Authenticated users)
    *   **Response (200)**: `{ ...userObject }`
*   `PUT /api/users/me` (Authenticated users)
    *   **Body**: `{ firstName, lastName, mobileNumber }`
    *   **Response (200)**: `{ ...userObject }`
*   `PUT /api/users/me/password` (Authenticated users)
    *   **Body**: `{ oldPassword, newPassword }`
    *   **Response (200)**: `200 OK`
*   `PUT /api/users/me/location` (Authenticated users, mainly for Workers)
    *   **Body**: `{ lat, lng }`
    *   **Response (200)**: `{ ...userObject }`

#### Issues (`/api/issues`)
*   `GET /api/issues` (Admin only)
    *   **Response (200)**: `[ { ...issueObject }, ... ]`
*   `GET /api/issues/reported` (Citizen only)
    *   Returns issues reported by the authenticated citizen.
    *   **Response (200)**: `[ { ...issueObject }, ... ]`
*   `GET /api/issues/assigned` (Worker only)
    *   Returns issues assigned to the authenticated worker.
    *   **Response (200)**: `[ { ...issueObject }, ... ]`
*   `GET /api/issues/user/:identifier` (Service role only)
    *   Returns issues for a specific user by email or mobile.
    *   **Response (200)**: `[ { ...issueObject }, ... ]`
*   `GET /api/issues/:id` (Authenticated users, with role-based access checks)
    *   **Response (200)**: `{ ...issueObject }`
*   `POST /api/issues` (Authenticated users)
    *   **Body**: `FormData` containing `description` (string), `location` (JSON string `{"lat": number, "lng": number}`), and `photos` (file array).
    *   **Backend Logic**: The backend receives this, calls the Gemini API for categorization, finds the nearest worker, and then creates the issue in the database.
    *   **Response (201)**: `{ ...issueObject }`
*   `POST /api/issues/:id/comments` (Authorized users)
    *   **Body**: `{ text: "comment_text" }`
    *   **Response (200)**: `{ ...issueObject }`
*   `PUT /api/issues/:id/status` (Admin/Worker only)
    *   **Body**: `{ status: "NewStatus" }`
    *   **Response (200)**: `{ ...issueObject }`
*   `PUT /api/issues/:id/assign` (Admin only)
    *   **Body**: `{ workerEmail: "worker@test.com" }`
    *   **Response (200)**: `{ ...issueObject }`
*   `PUT /api/issues/:id/resolve` (Citizen who reported it only)
    *   **Body**: `{ rating: 5 }`
    *   **Response (200)**: `{ ...issueObject }`

---

## ☁️ Deployment to Vercel

This Flask application is structured for easy deployment on Vercel.

1.  Push your code to a Git repository (GitHub, GitLab, etc.).
2.  Import the repository into Vercel. Vercel will automatically detect it as a Python project.
3.  **Configure Environment Variables**: In your Vercel project settings, add the `SECRET_KEY`, `DATABASE_URL` (from Vercel Postgres or another provider), and `GEMINI_API_KEY`.
4.  **Set Build Command**: In the "Build & Development Settings", set the **Build Command** to:
    ```sh
    flask db upgrade
    ```
    This ensures your production database schema is always up-to-date with your models on every deployment.
5.  Deploy! Vercel will handle the rest. Your API will be live at the provided Vercel domain.
