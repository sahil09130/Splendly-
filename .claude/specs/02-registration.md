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

### Verify (already exist)
- `templates/register.html` — Registration form with name, email, and password fields
- `templates/base.html` — Navbar already links to /register route
- `static/css/style.css` — Auth form styling (.auth-error, .form-input, .btn-submit) already complete

## Files to change

- `app.py` — Harden `/register` POST handler: input validation (8+ char password), input normalisation (strip whitespace, lowercase email), proper exception handling, connection cleanup, form value re-population on error
- `app.py` — Apply same email normalisation to `/login` for compatibility
- `templates/register.html` — Add form value preservation and minlength="8" client-side validation
- `.claude/specs/02-registration.md` — Update spec to reflect completed work

## Files to create

- `tests/test_registration.py` — Comprehensive test suite for registration flow

## New dependencies

No new dependencies. Uses existing werkzeug.security.generate_password_hash

## Rules for implementation

1. **Input validation**: All fields (name, email, password) are required; no registration without them
2. **Password strength**: Minimum 8 characters; validate on both server (required) and client (HTML5 minlength)
3. **Email normalisation**: Strip whitespace and convert to lowercase; prevents `test@x.com` and `TEST@X.COM` registering as different accounts
4. **Name normalisation**: Strip leading/trailing whitespace (no case change)
5. **Form value preservation**: On validation error, re-populate name and email fields; never show password
6. **Password hashing**: Always use werkzeug's `generate_password_hash()` — never store plaintext passwords
7. **Duplicate email prevention**: Catch `sqlite3.IntegrityError` on INSERT and display "Email already registered" error
8. **Error handling**: Display errors on the form without exposing database details
9. **Post-registration**: Redirect to /login after successful registration (user must log in)
10. **Database connection**: Use the `get_db()` function from database.db module; always close connections (use try/finally)
11. **Parameterized queries**: Use `?` placeholders to prevent SQL injection
12. **CSS consistency**: Use CSS variables from style.css (--ink-faint, --paper, --accent-2, etc.)
13. **Template inheritance**: Always extend base.html

## Definition of done

- [ ] User can navigate to /register and see the registration form
- [ ] Form has three fields: Full name, Email address, Password
- [ ] Password field has `minlength="8"` for client-side validation
- [ ] Form validates that all fields are required (shown as error on submission)
- [ ] Form rejects password shorter than 8 characters with error message
- [ ] User can enter valid data and submit the form successfully
- [ ] After successful registration, user is redirected to /login page
- [ ] If email already exists, error message "Email already registered" is displayed
- [ ] Email addresses are case-insensitive (TEST@X.COM and test@x.com are treated as duplicates)
- [ ] Form preserves name and email on validation error, but never shows password
- [ ] Whitespace is stripped from name and email inputs
- [ ] Password is hashed and stored securely (never plaintext in database)
- [ ] User can log in with their new account using the registered email and password
- [ ] Form styling matches the rest of the app (uses auth-section, auth-card, form-input classes)
- [ ] All registration tests pass: `pytest -v tests/test_registration.py`
