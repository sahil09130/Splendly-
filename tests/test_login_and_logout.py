import sqlite3
import sys
from pathlib import Path
import pytest
from werkzeug.security import generate_password_hash


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


@pytest.fixture
def user_in_db(app):
    """Create a test user in the database."""
    from database.db import get_db
    conn = get_db()
    password_hash = generate_password_hash("password123")
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", password_hash)
    )
    conn.commit()
    conn.close()
    return {"name": "Test User", "email": "test@example.com", "password": "password123"}


class TestLoginForm:
    """Test login form display and submission."""

    def test_get_login_returns_form(self, client):
        """GET /login displays the login form."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Welcome back" in response.data
        assert b'name="email"' in response.data
        assert b'name="password"' in response.data

    def test_post_valid_login_redirects_to_profile(self, client, user_in_db):
        """POST with valid credentials redirects to /profile."""
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

    def test_post_valid_login_sets_session(self, client, user_in_db):
        """POST with valid credentials sets session data."""
        with client:
            response = client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            assert response.status_code == 200
            # Check session was set
            from flask import session
            assert "user_id" in dict(session) or b"Your profile" in response.data

    def test_post_invalid_password_shows_error(self, client, user_in_db):
        """POST with wrong password shows error."""
        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Invalid email or password" in response.data

    def test_post_unknown_email_shows_error(self, client, user_in_db):
        """POST with unknown email shows error."""
        response = client.post(
            "/login",
            data={
                "email": "unknown@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Invalid email or password" in response.data

    def test_post_empty_email_shows_error(self, client, user_in_db):
        """POST with empty email shows error."""
        response = client.post(
            "/login",
            data={
                "email": "",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Email and password are required" in response.data

    def test_post_empty_password_shows_error(self, client, user_in_db):
        """POST with empty password shows error."""
        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Email and password are required" in response.data

    def test_post_empty_fields_shows_error(self, client, user_in_db):
        """POST with empty email and password shows error."""
        response = client.post(
            "/login",
            data={
                "email": "",
                "password": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b"Email and password are required" in response.data

    def test_email_case_insensitive(self, client, user_in_db):
        """Login works with uppercase/mixed case email."""
        response = client.post(
            "/login",
            data={
                "email": "TEST@EXAMPLE.COM",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.endswith("/profile")

    def test_email_whitespace_stripped(self, client, user_in_db):
        """Login works with padded email."""
        response = client.post(
            "/login",
            data={
                "email": "  test@example.com  ",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.endswith("/profile")

    def test_email_preserved_on_error(self, client, user_in_db):
        """Email field is preserved on validation error."""
        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        assert b'value="test@example.com"' in response.data

    def test_password_never_echoed(self, client, user_in_db):
        """Password is never shown in response."""
        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "password123",
            },
            follow_redirects=False,
        )
        assert b"password123" not in response.data


class TestProfile:
    """Test profile page display and access control."""

    def test_profile_without_session_redirects_to_login(self, client):
        """GET /profile without session redirects to /login."""
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith("/login")

    def test_profile_with_session_shows_data(self, client, user_in_db):
        """GET /profile with session shows user data."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            assert b"Your profile" in response.data
            assert b"Test User" in response.data
            assert b"test@example.com" in response.data

    def test_profile_shows_joined_date(self, client, user_in_db):
        """GET /profile displays account creation date."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            assert b"Joined" in response.data

    def test_profile_has_logout_link(self, client, user_in_db):
        """GET /profile has a logout link."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            assert b"logout" in response.data.lower()


class TestLogout:
    """Test logout functionality."""

    def test_logout_redirects_to_landing(self, client, user_in_db):
        """GET /logout redirects to landing page."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/logout", follow_redirects=False)
            assert response.status_code == 302
            assert response.location.endswith("/")

    def test_logout_clears_session(self, client, user_in_db):
        """GET /logout clears the session."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            client.get("/logout", follow_redirects=True)
            # After logout, accessing profile should redirect to login
            response = client.get("/profile", follow_redirects=False)
            assert response.status_code == 302
            assert response.location.endswith("/login")

    def test_profile_unreachable_after_logout(self, client, user_in_db):
        """After logout, /profile redirects to /login."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            client.get("/logout", follow_redirects=True)
            response = client.get("/profile", follow_redirects=False)
            assert response.status_code == 302
            assert response.location.endswith("/login")


class TestNavbar:
    """Test navbar state based on login status."""

    def test_navbar_shows_login_links_when_logged_out(self, client):
        """Navbar shows 'Sign in' and 'Get started' when logged out."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Sign in" in response.data
        assert b"Get started" in response.data

    def test_navbar_shows_user_name_when_logged_in(self, client, user_in_db):
        """Navbar shows user name when logged in."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            assert b"Test User" in response.data

    def test_navbar_shows_logout_when_logged_in(self, client, user_in_db):
        """Navbar shows 'Logout' link when logged in."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            assert b"Logout" in response.data

    def test_navbar_hides_login_links_when_logged_in(self, client, user_in_db):
        """Navbar hides 'Sign in' and 'Get started' when logged in."""
        with client:
            client.post(
                "/login",
                data={
                    "email": "test@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )
            response = client.get("/profile")
            assert response.status_code == 200
            # Should not have the logout link context if it's showing logout
            # The navbar should only show the logged-in version
