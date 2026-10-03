# Spec: Profile Page Design

## Overview
Replace the `/profile` placeholder ("Profile page — coming in Step 4") with a real, designed profile page. Login and registration already redirect to `/profile`, so this is the first screen a logged-in user sees. It shows the user's account details (name, email, member since), a summary of their spending (total spent, number of expenses, top category), a per-category breakdown, and a list of recent expenses, all read from the existing `users` and `expenses` tables. It is read-only: adding, editing and deleting expenses come in Steps 7–9.

## Depends on
- Step 1 — Database setup (`users`, `expenses`, `get_db`, `seed_db`)
- Step 2 — Registration
- Step 3 — Login and Logout (session `user_id`)

## Routes
- GET /profile — render the profile page for the current user; redirect to `/login` if not logged in — logged-in

No other new routes. The existing `/profile` placeholder in `app.py` is replaced in place. Existing links to `add_expense`, `edit_expense` and `delete_expense` stay as placeholders.

## Database changes
No database changes. Existing schema in `database/db.py` is sufficient (`users.id/name/email/created_at`, `expenses.user_id/amount/category/date/description`).

New query helpers to add in `database/db.py` (all parameterised, each opens and closes its own connection via `get_db()`):
- `get_user_by_id(user_id)` — returns the user row or `None`
- `get_expense_summary(user_id)` — total amount, expense count, and top category (by total) for the user; zeros/`None` when there are no expenses
- `get_category_totals(user_id)` — list of `(category, total)` ordered by total descending
- `get_recent_expenses(user_id, limit=10)` — latest expenses ordered by `date DESC, id DESC`

## Templates
- Create: `templates/profile.html` — extends `base.html`, sets `{% block title %}`, contains:
  - Header card: avatar circle with the user's initial, name, email, "Member since <Month YYYY>"
  - Stats row: Total spent, Number of expenses, Top category
  - Category breakdown: one row per category with amount and a proportional bar (width set via inline `style="width: N%"` from computed percentage)
  - Recent expenses table: date, description, category badge, amount
  - Empty state when the user has no expenses (message only, no add link target change)
- Modify: `templates/base.html` — when logged in, add a "Profile" link in `.nav-links` before "Log out"

## Files to change
- `app.py` — implement `profile()` (auth guard, fetch data, render template); import the new db helpers
- `database/db.py` — add the query helpers listed above
- `templates/base.html` — add Profile nav link for logged-in users
- `static/css/style.css` — add profile page styles (new section at the end)

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (no change here; never expose or render `password_hash`)
- Use CSS variables - never hardcode hex values (reuse `--accent`, `--paper-card`, `--border`, `--radius-md`, etc.; add new variables to `:root` if truly needed)
- All templates extend base.html
- Replace the existing `/profile` route in place; do not add a duplicate
- If `session["user_id"]` refers to a user that no longer exists, clear the session and redirect to `/login`
- Scope every expense query by the logged-in user's `user_id`; never trust a user id from the URL or form
- Format amounts with the ₹ symbol and two decimals; format via a Jinja expression (e.g. `'%.2f'|format(x)`)
- Rely on Jinja autoescaping for names, emails and descriptions; do not use `|safe`
- Follow the existing visual language (DM Serif Display headings, DM Sans body, paper/ink palette) and make the layout responsive down to mobile width
- Keep JavaScript out unless necessary; no new JS needed for this step

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Logging in as `demo@spendly.com` / `demo123` lands on `/profile` showing "Demo User", the email, and a "Member since" date
- [ ] Stats show total spent ₹322.24, 8 expenses, and top category "Bills" for the seeded demo user
- [ ] Category breakdown lists all 7 seeded categories in descending order of total, with bars proportional to share
- [ ] Recent expenses table shows the seeded expenses newest-first with date, description, category and amount
- [ ] A newly registered user with no expenses sees zeroed stats and an empty-state message, with no errors
- [ ] A user only ever sees their own expenses (verify by registering a second user)
- [ ] Navbar shows "Profile" and "Log out" when logged in, and "Sign in"/"Get started" when logged out
- [ ] Page renders cleanly at ~375px width and at desktop width with no horizontal scroll
- [ ] No hardcoded hex colours in the new CSS; all templates extend `base.html`
- [ ] App starts with `python app.py` without errors
