import sqlite3
import sys
from pathlib import Path
import pytest
from werkzeug.security import check_password_hash


@pytest.fixture
def app(monkeypatch, tmp_path):
    """Create and configure a test Flask app with isolated database."""
    db_path = tmp_path / "test.db"

    # Add the project root to sys.path so imports work correctly
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from database import db as db_module
    monkeypatch.setattr(db_module, "DB_PATH", db_path)

    from app import app as flask_app
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        from database.db import init_db
        init_db()

    return flask_app


@pytest.fixture
def client(app):
    """Test client for the Flask app."""
    return app.test_client()


class TestRegistrationForm:
    """Test registration form display and submission."""

    def test_get_register_returns_form(self, client):
        """GET /register displays the registration form."""
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Create your account" in response.data
        assert b'name="name"' in response.data
        assert b'name="email"' in response.data
        assert b'name="password"' in response.data

    def test_post_valid_registration_redirects_to_login(self, client):
        """POST with valid data redirects to /login."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.endswith("/login")

    def test_valid_registration_creates_user(self, client, app):
        """Valid registration creates a user in the database."""
        client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        from database.db import get_db
        conn = get_db()
        user = conn.execute(
            "SELECT name, email, password_hash FROM users WHERE email = ?",
            ("test@example.com",),
        ).fetchone()
        conn.close()

        assert user is not None
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
        assert user["password_hash"] != "password123"
        assert check_password_hash(user["password_hash"], "password123")


class TestRegistrationValidation:
    """Test input validation."""

    def test_missing_name_shows_error(self, client):
        """Missing name shows 'All fields are required' error."""
        response = client.post(
            "/register",
            data={
                "name": "",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert b"All fields are required" in response.data

    def test_missing_email_shows_error(self, client):
        """Missing email shows error."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        assert b"All fields are required" in response.data

    def test_missing_password_shows_error(self, client):
        """Missing password shows error."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "",
            },
        )
        assert response.status_code == 200
        assert b"All fields are required" in response.data

    def test_short_password_shows_error(self, client):
        """Password shorter than 8 characters shows error."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 200
        assert b"Password must be at least 8 characters" in response.data

    def test_no_user_created_on_validation_error(self, client, app):
        """No user is created when validation fails."""
        client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "short",
            },
        )

        from database.db import get_db
        conn = get_db()
        user_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
        conn.close()

        assert user_count["count"] == 0


class TestRegistrationErrors:
    """Test error handling."""

    def test_duplicate_email_shows_error(self, client):
        """Registering with an existing email shows error."""
        client.post(
            "/register",
            data={
                "name": "First User",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        response = client.post(
            "/register",
            data={
                "name": "Second User",
                "email": "test@example.com",
                "password": "password456",
            },
        )

        assert response.status_code == 200
        assert b"Email already registered" in response.data

    def test_duplicate_email_case_insensitive(self, client):
        """Email is case-insensitive for duplicates."""
        client.post(
            "/register",
            data={
                "name": "First User",
                "email": "Test@Example.com",
                "password": "password123",
            },
        )

        response = client.post(
            "/register",
            data={
                "name": "Second User",
                "email": "test@example.com",
                "password": "password456",
            },
        )

        assert response.status_code == 200
        assert b"Email already registered" in response.data

    def test_form_values_preserved_on_error(self, client):
        """Form name and email are re-populated after validation error."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 200
        assert b'value="Test User"' in response.data
        assert b'value="test@example.com"' in response.data

    def test_password_not_shown_in_error(self, client):
        """Password value is never re-populated on error."""
        response = client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert b'value="password123"' not in response.data


class TestRegistrationFlow:
    """Test end-to-end registration flow."""

    def test_registered_user_can_login(self, client):
        """User can log in after registering."""
        client.post(
            "/register",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.endswith("/profile")

    def test_whitespace_is_stripped(self, client, app):
        """Name and email have whitespace stripped."""
        client.post(
            "/register",
            data={
                "name": "  Test User  ",
                "email": "  test@example.com  ",
                "password": "password123",
            },
        )

        from database.db import get_db
        conn = get_db()
        user = conn.execute(
            "SELECT name, email FROM users WHERE email = ?",
            ("test@example.com",),
        ).fetchone()
        conn.close()

        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
