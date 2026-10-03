# Spec: Registration

## Overview
Lets a new visitor create a Spendly account. The `/register` page already renders a form, but the route only accepts GET and the form posts nowhere. This step adds POST handling: validate the input, hash the password with werkzeug, insert a row into the existing `users` table, and redirect to the login page. It is the first feature that writes user data and unblocks login (Step 3) and everything behind it.

## Depends on
- Step 1: Database setup (`get_db()`, `init_db()`, `users` table with a UNIQUE `email`).

## Routes
- GET /register - render the registration form - public (unchanged)
- POST /register - validate form, create user, redirect to `/login` on success, re-render the form with an error on failure - public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email` UNIQUE, `password_hash`, `created_at`) is sufficient.

A helper is added to `database/db.py` (no schema change):
- `create_user(name, email, password_hash)` - inserts a user and returns the new id; raises `sqlite3.IntegrityError` on a duplicate email.
- `get_user_by_email(email)` - returns a `sqlite3.Row` or `None` (also useful for Step 3).

## Templates
- Create: none
- Modify:
  - `templates/register.html` - keep the existing form; repopulate `name` and `email` with the submitted values after a failed submit (never the password); use `url_for('register')` for the form action instead of the hardcoded `/register`; add `minlength="8"` to the password input.

## Files to change
- `app.py` - change `register` to accept `GET` and `POST`; add form validation and user creation.
- `database/db.py` - add `create_user` and `get_user_by_email`.
- `templates/register.html` - as described above.
- `static/css/style.css` - only if the existing `.auth-error` style is missing or needs a tweak (use CSS variables).

## Files to create
- `tests/test_registration.py` - pytest tests for the registration flow (the `tests/` directory does not exist yet).

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log plaintext
- Use CSS variables - never hardcode hex values
- All templates extend `base.html`
- Replace the existing `/register` route in place; do not add a duplicate
- Validation rules (server-side, regardless of HTML attributes):
  - `name`: required, stripped, non-empty
  - `email`: required, stripped, lowercased, must contain `@` with text on both sides
  - `password`: required, at least 8 characters
- A duplicate email must show a friendly error ("An account with that email already exists"), not a 500. Rely on the UNIQUE constraint by catching `sqlite3.IntegrityError`, so there is no check-then-insert race.
- Use `get_db()` and close the connection in a `finally` block, matching the style in `database/db.py`
- Do not log the user in on registration; redirect to `url_for('login')` (sessions arrive in Step 3)
- Do not implement login, logout or sessions in this step

## Definition of done
- [ ] `GET /register` still renders the form with status 200
- [ ] Submitting valid name, email and password creates a row in `users` and redirects (302) to `/login`
- [ ] The stored `password_hash` is not the plaintext password and passes `check_password_hash`
- [ ] Registering the same email again (including with different casing) re-renders the form with a duplicate-email error and creates no second row
- [ ] An empty name, invalid email, or password shorter than 8 characters re-renders the form with an error and creates no row
- [ ] After a failed submit, the name and email fields keep their values and the password field is empty
- [ ] The seeded demo user (`demo@spendly.com`) is unaffected
- [ ] `pytest tests/test_registration.py` passes
- [ ] The app starts with `python app.py` with no errors
