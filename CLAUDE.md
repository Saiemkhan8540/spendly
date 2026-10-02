# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this code in this repository.

## Project

"Spendly" — a Flask expense tracker built as a step-by-step teaching project. Much of it is intentionally unimplemented scaffolding that gets filled in step by step.

## Commands

```
source venv/bin/activate
pip install -r requirements.txt
python app.py                  # dev server, debug mode, http://localhost:5001
pytest                         # run all tests (pytest + pytest-flask are installed)
pytest path/to/test.py::test_name   # single test
```

No tests, linter, or build step exist yet.

## Architecture

- `app.py` — single Flask app with all routes. Implemented routes only render templates (`/`, `/register`, `/login`, `/terms`, `/privacy`). The routes `/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete` are placeholders returning strings, each labelled with the step that implements it ("Step 3", "Step 4", "Step 7"–"Step 9"). Replace these in place rather than adding duplicates.
- `database/db.py` — currently only a comment stub describing the planned contract (Step 1): `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (sample data). `database/__init__.py` is empty. The SQLite file `expense_tracker.db` is gitignored.
- `templates/` — all pages extend `base.html` (navbar, Google Fonts DM Serif Display / DM Sans, `{% block title %}` and `{% block head %}`). Link with `url_for(...)`, including static files.
- `static/css/style.css` — one shared stylesheet for all pages (landing page styles included). `static/js/main.js` is currently a one-line stub.
- Register and login forms have no POST handling yet; the routes accept GET only.
