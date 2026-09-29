# Spec: Login and Logout

## Overview

Step 3 implements user authentication with login and logout functionality. Users can sign in with their registered email and password, which establishes a secure session. Once logged in, users see their profile page and a personalized navbar. The logout feature clears the session and returns users to the landing page. This enables secure user sessions and establishes the foundation for user-specific features (profile, expense management).

## Depends on

- Step 1: Database setup (users table with password hashing support)
- Step 2: Registration (users can create accounts)

## Routes

- `GET /login` — Display login form — public
- `POST /login` — Handle login form submission with validation — public
- `GET /logout` — Clear session and redirect to landing page — logged-in
- `GET /profile` — Display user profile page with logged-in content — logged-in

## Database changes

No new database changes. Uses existing `users` table:
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `email` (TEXT NOT NULL UNIQUE)
- `password_hash` (TEXT NOT NULL)
- `created_at` (TEXT NOT NULL DEFAULT (datetime('now')))

## Templates

### Verify (already exist)
- `templates/login.html` — Login form with email and password fields (may need minor fixes)
- `templates/base.html` — Navbar needs conditional rendering for logged-in state

### Create
- `templates/profile.html` — User profile page showing name, email, joined date, and logout button

### Modify
- `templates/base.html` — Add conditional navbar rendering:
  - If logged-in: show user name and logout link
  - If logged-out: show "Sign in" and "Get started" links

## Files to change

- `app.py` — Harden `/login` POST handler: input normalisation (strip, lowercase email), proper error handling, error message on form, connection cleanup
- `app.py` — Replace `/profile` placeholder with proper template rendering
- `templates/base.html` — Update navbar to show logged-in state (check for `user_id` in session)
- `templates/login.html` — Add form value preservation for email on validation error

## Files to create

- `templates/profile.html` — User profile page template
- `tests/test_login_and_logout.py` — Comprehensive test suite for login/logout flow

## New dependencies

No new dependencies. Uses existing werkzeug.security.check_password_hash and Flask session management.

## Rules for implementation

1. **Input validation**: Email and password fields are required; reject empty submissions
2. **Email normalisation**: Strip whitespace and convert to lowercase (consistent with registration)
3. **Password verification**: Use werkzeug's `check_password_hash()` to verify passwords
4. **Session management**: Store `user_id` and `user_name` in session on successful login
5. **Form value preservation**: On login error, re-populate email field; never show password
6. **Error messages**: Display "Invalid email or password" without revealing which field failed (security best practice)
7. **Logout functionality**: Use `session.clear()` to completely clear all session data
8. **Profile protection**: Always check for `user_id` in session before rendering protected pages
9. **Navbar state**: Conditionally render navbar links based on session state (logged-in vs logged-out)
10. **Database connection**: Use the `get_db()` function from database.db module; always close connections (use try/finally)
11. **Parameterized queries**: Use `?` placeholders to prevent SQL injection
12. **CSS consistency**: Use CSS variables from style.css (--ink-faint, --paper, --accent-2, etc.)
13. **Template inheritance**: Always extend base.html

## Definition of done

- [ ] User can navigate to /login and see the login form
- [ ] Form has two fields: Email address and Password
- [ ] Form validates that both fields are required (shown as error on submission)
- [ ] User can enter valid registered credentials and submit the form successfully
- [ ] After successful login, user is redirected to /profile page
- [ ] If email/password is invalid, error message "Invalid email or password" is displayed
- [ ] Email addresses are case-insensitive (TEST@X.COM and test@x.com work the same)
- [ ] Form preserves email on validation error, but never shows password
- [ ] Whitespace is stripped from email input
- [ ] Navbar displays user's name and logout link when user is logged-in
- [ ] User can click logout and return to landing page
- [ ] After logout, session is cleared and user cannot access profile without logging in again
- [ ] Profile page displays user's name, email, and account creation date
- [ ] Profile page has a logout button or link
- [ ] If user navigates to /profile without being logged-in, they are redirected to /login
- [ ] Form styling matches the rest of the app (uses auth-section, auth-card, form-input classes)
- [ ] All login/logout tests pass: `pytest -v tests/test_login_and_logout.py`
