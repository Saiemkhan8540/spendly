# Spec: Backend Routes for Profile Page

## Overview
Step 4 built the profile page and already wired it to live data (`get_user_by_id`, `get_expense_summary`, `get_category_totals`, `get_recent_expenses`), but it always shows all-time figures and the last 10 expenses, and the aggregation logic (category percentages, member-since formatting) lives inside the route function. This step hardens and extends the profile backend: `/profile` accepts optional `from` / `to` date query parameters that scope the summary, category breakdown and expense list to a date range, the view logic moves out of the route into testable helpers, and a small JSON endpoint exposes the same data for future dynamic UI. It prepares the data layer that Steps 7-9 (add/edit/delete expenses) will feed.

## Depends on
- Step 1 — Database setup (`users`, `expenses`, `get_db`, `seed_db`)
- Step 2 — Registration
- Step 3 — Login and Logout (session `user_id`)
- Step 4 — Profile page design (`/profile`, `profile.html`, existing db query helpers)

## Routes
- GET /profile — existing route, extended: optional `?from=YYYY-MM-DD&to=YYYY-MM-DD` filters all three sections; invalid or reversed dates are ignored with an inline message (no 500); redirect to `/login` if not logged in — logged-in
- GET /profile/data — JSON of the same summary, category totals and recent expenses for the logged-in user, honouring the same `from` / `to` params; returns `401` JSON `{"error": "Not logged in"}` when logged out (no redirect) — logged-in

The `/profile` route is modified in place; do not add a duplicate. `add_expense`, `edit_expense` and `delete_expense` stay as placeholders.

## Database changes
No database changes. Existing schema in `database/db.py` is sufficient (`expenses.date` is stored as ISO `YYYY-MM-DD` text, so range comparisons work lexicographically).

Modify existing helpers in `database/db.py` to take optional `date_from=None, date_to=None` arguments (parameterised; add the `AND date >= ?` / `AND date <= ?` clauses only when a bound is given):
- `get_expense_summary(user_id, date_from=None, date_to=None)`
- `get_category_totals(user_id, date_from=None, date_to=None)`
- `get_recent_expenses(user_id, limit=10, date_from=None, date_to=None)`

Add one new helper:
- `get_profile_data(user_id, date_from=None, date_to=None)` — returns a dict `{summary, categories, recent}` where `categories` already includes the `percent` of total (rounded to 1 decimal, `0` when total is 0). Used by both routes so the logic exists once.

## Templates
- Create: none
- Modify: `templates/profile.html` — add a small filter form (From, To, Apply, Clear) above the stats row that submits via GET to `url_for('profile')`, repopulates the submitted dates, and shows the validation message when dates were rejected. Show "No expenses in this range" in the existing empty states when a filter is active.

## Files to change
- `app.py` — add a `parse_date_range(args)` helper (validates ISO dates, rejects `from > to`); slim `profile()` to auth guard + `get_profile_data` + render; add `profile_data()` JSON route; remove the inline percent calculation
- `database/db.py` — optional date params on the three helpers; add `get_profile_data`
- `templates/profile.html` — filter form and range-aware empty states
- `static/css/style.css` — styles for the filter form (new section at the end)

## Files to create
- `tests/test_profile_backend.py` — covers filtering, validation, auth and JSON shape

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only; never interpolate `from` / `to` into SQL
- Passwords hashed with werkzeug (no change; never include `password_hash` in any response, including the JSON endpoint)
- Use CSS variables - never hardcode hex values
- All templates extend base.html
- Scope every query by `session["user_id"]`; never accept a user id from the URL, query string or form
- Validate dates with `datetime.strptime(value, "%Y-%m-%d")`; on invalid input ignore that bound and show a message, never raise
- Keep the existing `/profile` behaviour unchanged when no query params are given (same numbers as Step 4)
- JSON amounts are numbers rounded to 2 decimals; dates are ISO strings
- Keep JavaScript out; the filter form is a plain GET form
- Existing tests (`test_registration`, `test_login_logout`, `test_profile`) must still pass

## Definition of done
- [ ] `/profile` with no params still shows total ₹322.24, 8 expenses, top category "Bills" for the demo user
- [ ] `/profile?from=<day 10>&to=<day 18>` (current month, ISO dates) shows only expenses inside that range, with matching stats and category bars
- [ ] Only `from` or only `to` works as an open-ended range
- [ ] `/profile?from=garbage` and `/profile?from=2026-10-20&to=2026-10-01` return 200 with an inline message and unfiltered/ignored bounds, never a 500
- [ ] A range with no matches shows zeroed stats and the "No expenses in this range" empty state
- [ ] The filter form repopulates submitted dates; Clear returns to `/profile`
- [ ] `GET /profile/data` while logged in returns JSON with `summary`, `categories` and `recent` matching the HTML page for the same params
- [ ] `GET /profile/data` while logged out returns 401 JSON and `/profile` still redirects to `/login`
- [ ] A second registered user never sees the demo user's expenses on either route
- [ ] `pytest` passes, including the new `tests/test_profile_backend.py`
- [ ] No hardcoded hex colours in new CSS; app starts with `python app.py` without errors
