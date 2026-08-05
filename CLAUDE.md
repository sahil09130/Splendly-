# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly is a Flask expense tracker application designed as a step-by-step student learning project. The app allows users to register, log in, track expenses, and manage their financial data.

## Development Commands

**Run the dev server:**
```bash
python app.py
```
The app runs on `http://localhost:5001` with debug mode enabled.

**Run tests:**
```bash
pytest
pytest -v                    # verbose output
pytest tests/test_name.py    # single test file
pytest -k test_function      # run specific test by name
```

The project includes pytest and pytest-flask for testing.

## Architecture

**Flask App Structure (app.py)**
- Entry point with route definitions
- Routes organized by feature: landing page, auth (register/login), legal pages (terms/privacy), expense CRUD (add/edit/delete), and profile
- Placeholder routes with "coming in Step X" comments indicate the intended learning progression (Steps 1–9)
- Runs on port 5001 with debug=True

**Database Module (database/db.py)**
- Students implement this module (Step 1) with three functions:
  - `get_db()` — returns SQLite connection with row_factory and foreign keys enabled
  - `init_db()` — creates tables using CREATE TABLE IF NOT EXISTS
  - `seed_db()` — inserts sample data for development
- Expected to use SQLite (see .gitignore: expense_tracker.db)

**Templates (templates/)**
- Base template inheritance via `base.html`
- Includes navbar, main content block, and footer with legal links
- Auth pages (register.html, login.html), legal pages (terms.html, privacy.html), landing page
- Forms use POST method to `/register` and `/login` routes (handlers not yet implemented)

**Styling (static/css/)**
- `style.css` — main stylesheet with CSS custom properties (--ink-faint, --paper, --accent-2, etc.)
- `landing.css` — landing page specific styles
- Responsive design using flexbox/grid

**Client Code (static/js/main.js)**
- Currently empty; students add JavaScript as features are built

## Key Patterns & Notes

- **Templating**: Uses Jinja2 with `url_for()` for dynamic route generation
- **CSS variables**: Theme uses a custom property system; maintain consistency with existing color names
- **Learning progression**: Routes reference "Step X" indicating this is scaffolded coursework; future implementations should follow the same pattern
- **Database pattern**: When database/db.py is implemented, it should follow SQLite conventions with row factory and foreign key constraints enabled

## Environment

- Python 3.x
- Virtual environment at `venv/` (in .gitignore)
- Dependencies: Flask 3.1.3, Werkzeug 3.1.6, pytest 8.3.5, pytest-flask 1.3.0
