# Spec: Login and Logout

## Overview
Lets a registered user sign in and out. `/login` currently renders a form that posts nowhere, and `/logout` is a placeholder string. This step verifies the submitted credentials against the `users` table, stores the user's id in Flask's signed session cookie, and clears it on logout. It also makes the navbar reflect auth state. It is the first feature that gives the app a notion of "who is logged in", which the profile (Step 4) and expense routes (Steps 7-9) depend on.

## Depends on
- Step 1: Database setup (`users` table, `get_db()`).
- Step 2: Registration (`create_user()`, `get_user_by_email()`, hashed passwords, redirect to `/login` after signup).

## Routes
- GET /login - render the sign-in form; redirect to `/profile` if already logged in - public
- POST /login - verify credentials, start a session, redirect to `/profile` on success, re-render the form with an error on failure - public
- GET /logout - clear the session and redirect to `/` - public (safe to call when logged out)
- GET /register - redirect to `/profile` if already logged in (behaviour change to the existing route) - public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email` UNIQUE, `password_hash`, `created_at`) is sufficient. `get_user_by_email()` already exists in `database/db.py` from Step 2 and is reused; no new DB functions are needed.

## Templates
- Create: none
- Modify:
  - `templates/login.html` - form action via `url_for('login')`; repopulate `email` after a failed submit (never the password).
  - `templates/base.html` - navbar: when `session.user_id` is set, show a "Log out" link (`url_for('logout')`) instead of "Sign in" / "Get started"; otherwise keep the current links.

## Files to change
- `app.py` - set `app.secret_key`; make `login` accept GET and POST; implement `logout`; redirect logged-in users away from `/login` and `/register`.
- `templates/login.html` - as above.
- `templates/base.html` - as above.
- `tests/` - none modified (new file below).

## Files to create
- `tests/test_login_logout.py` - pytest tests for login and logout.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug; verify with `check_password_hash`, never compare plaintext
- Use CSS variables - never hardcode hex values
- All templates extend base.html
- Replace the existing `/login` and `/logout` routes in place; do not add duplicates
- `app.secret_key` is read from the `SECRET_KEY` environment variable with a clearly named development fallback; do not commit a real secret
- Normalise the email the same way registration does (strip, lowercase) before lookup
- Use a single generic error for both unknown email and wrong password ("Invalid email or password.") so the form does not reveal which emails are registered
- On successful login call `session.clear()` first, then set `session["user_id"] = user["id"]`; store only the id, never the hash or other user fields
- Redirect target after login is always `url_for('profile')`; do not honour a `next` parameter (avoids open redirects)
- Logout is a GET link, matching the existing placeholder route; it must work when no one is logged in
- Do not implement route protection (`login_required`), profile content, flash messages, "remember me" or password reset in this step

## Definition of done
- [ ] `GET /login` renders the form with status 200 when logged out
- [ ] Logging in as `demo@spendly.com` / `demo123` redirects (302) to `/profile`
- [ ] Email is matched case-insensitively and ignores surrounding whitespace
- [ ] A wrong password and an unregistered email both re-render the form (200) with the same "Invalid email or password." error and no session
- [ ] After a failed submit the email field keeps its value and the password field is empty
- [ ] A user created through `/register` can immediately log in with the same credentials
- [ ] After login, `session["user_id"]` equals the user's id and nothing else about the user is stored in the session
- [ ] After login the navbar shows "Log out" and hides "Sign in" / "Get started"; when logged out it shows the original links
- [ ] Visiting `/login` or `/register` while logged in redirects to `/profile`
- [ ] `GET /logout` clears the session and redirects to `/`; the navbar returns to the logged-out links
- [ ] `GET /logout` while logged out redirects to `/` without error
- [ ] `python -m pytest tests/test_login_logout.py` passes and the Step 2 tests still pass
- [ ] The app starts with `python app.py` with no errors
