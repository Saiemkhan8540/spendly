import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import (
    create_user,
    get_db,
    get_profile_data,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key")

with app.app_context():
    init_db()
    seed_db()


def parse_date_range(args):
    """Return (date_from, date_to, error) from ?from= / ?to= query args.

    Invalid bounds are dropped; a reversed range drops both. Never raises.
    """
    bounds = {}
    error = None
    for key in ("from", "to"):
        value = args.get(key, "").strip()
        if not value:
            continue
        try:
            datetime.strptime(value, "%Y-%m-%d")
            bounds[key] = value
        except ValueError:
            error = "Ignored an invalid date. Use the YYYY-MM-DD format."
    date_from, date_to = bounds.get("from"), bounds.get("to")
    if date_from and date_to and date_from > date_to:
        return None, None, "The start date is after the end date, so the filter was ignored."
    return date_from, date_to, error


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    local, _, domain = email.partition("@")
    if not name:
        error = "Name is required."
    elif not local or not domain:
        error = "Enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    else:
        error = None

    if error is None:
        try:
            create_user(name, email, generate_password_hash(password))
        except sqlite3.IntegrityError:
            error = "An account with that email already exists."
        else:
            return redirect(url_for("login"))

    return render_template("register.html", error=error, name=name, email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template(
            "login.html", error="Invalid email or password.", email=email
        )

    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    date_from, date_to, range_error = parse_date_range(request.args)
    data = get_profile_data(user_id, date_from, date_to)

    try:
        member_since = datetime.strptime(
            user["created_at"], "%Y-%m-%d %H:%M:%S"
        ).strftime("%B %Y")
    except (TypeError, ValueError):
        member_since = user["created_at"]

    return render_template(
        "profile.html",
        user=user,
        initial=user["name"][:1].upper(),
        member_since=member_since,
        summary=data["summary"],
        categories=data["categories"],
        recent=data["recent"],
        date_from=date_from or request.args.get("from", ""),
        date_to=date_to or request.args.get("to", ""),
        filtered=bool(date_from or date_to),
        range_error=range_error,
    )


@app.route("/profile/data")
def profile_data():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(error="Not logged in"), 401

    date_from, date_to, _ = parse_date_range(request.args)
    data = get_profile_data(user_id, date_from, date_to)
    data["summary"]["total"] = round(data["summary"]["total"], 2)
    for c in data["categories"]:
        c["total"] = round(c["total"], 2)
    for e in data["recent"]:
        e["amount"] = round(e["amount"], 2)
    return jsonify(data)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
