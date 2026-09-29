# Spec: Registration

## Overview

Step 2 implements user registration with email and password validation. Users can create an account by providing their name, email, and password. The system validates input, hashes passwords securely using werkzeug, checks for duplicate emails, and redirects users to login after successful registration. This is a foundational auth feature that enables user management for the expense tracker.

## Depends on

- Step 1: Database setup (users table with email UNIQUE constraint, password hashing support)

## Routes

- `POST /register` — Handle registration form submission with validation — public
- `GET /register` — Display registration form — public

## Database changes

No new database changes. Uses existing `users` table created in Step 1:
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `email` (TEXT NOT NULL UNIQUE)
- `password_hash` (TEXT NOT NULL)
- `created_at` (TEXT NOT NULL DEFAULT (datetime('now')))

## Templates

### Create
- `templates/register.html` — Registration form with name, email, and password fields

### Modify
- `templates/base.html` — Ensure navbar links to /register route
- `static/css/style.css` — Ensure auth form styling is complete

## Files to change

- `app.py` — Add POST handler for /register route with validation and user insertion

## Files to create

- `templates/register.html` — Registration form template

## New dependencies

No new dependencies. Uses existing werkzeug.security.generate_password_hash

## Rules for implementation

1. **Input validation**: All fields (name, email, password) are required; no registration without them
2. **Password hashing**: Always use werkzeug's `generate_password_hash()` — never store plaintext passwords
3. **Duplicate email prevention**: Catch `IntegrityError` on INSERT and display "Email already registered" error
4. **Error handling**: Display errors on the form without exposing database details
5. **Post-registration**: Redirect to /login after successful registration (user must log in)
6. **Database connection**: Use the `get_db()` function from database.db module; always close connections
7. **Parameterized queries**: Use `?` placeholders to prevent SQL injection
8. **CSS consistency**: Use CSS variables from style.css (--ink-faint, --paper, --accent-2, etc.)
9. **Template inheritance**: Always extend base.html

## Definition of done

- [ ] User can navigate to /register and see the registration form
- [ ] Form has three fields: Full name, Email address, Password
- [ ] Form validates that all fields are required (shown as error on submission)
- [ ] User can enter valid data and submit the form successfully
- [ ] After successful registration, user is redirected to /login page
- [ ] If email already exists, error message "Email already registered" is displayed
- [ ] Password is hashed and stored securely (never plaintext in database)
- [ ] User can log in with their new account using the registered email and password
- [ ] Form styling matches the rest of the app (uses auth-section, auth-card, form-input classes)
