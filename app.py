import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ml_model.predictor import make_prediction
from ml_model.train_model import train_model

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ecowise-local-secret")
DB_PATH = os.path.join(app.root_path, "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS Users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ConsumptionData (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          plastic_usage REAL,
          food_delivery_frequency REAL,
          shopping_frequency REAL,
          recycling_habits REAL,
          reusable_item_usage REAL,
          timestamp TEXT,
          FOREIGN KEY(user_id) REFERENCES Users(id)
        );

        CREATE TABLE IF NOT EXISTS WastePredictions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          consumption_id INTEGER,
          waste_level TEXT,
          waste_score REAL,
          carbon_footprint REAL,
          monthly_waste_estimate REAL,
          probability_low REAL,
          probability_medium REAL,
          probability_high REAL,
          prediction_date TEXT,
          FOREIGN KEY(user_id) REFERENCES Users(id)
        );

        CREATE TABLE IF NOT EXISTS Recommendations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          recommendation_text TEXT,
          category TEXT,
          created_at TEXT,
          FOREIGN KEY(user_id) REFERENCES Users(id)
        );
        """
    )
    existing = conn.execute("SELECT id FROM Users WHERE email = ?", ("admin@ecowise.local",)).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@ecowise.local", generate_password_hash("admin123")),
        )
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM Users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return user


@app.route("/")
def index():
    return render_template("index.html", user=current_user())


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not username or not email or len(password) < 6:
            flash("Enter a username, valid email, and password with at least 6 characters.", "danger")
            return render_template("signup.html")
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                (username, email, generate_password_hash(password)),
            )
            conn.commit()
            conn.close()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())


@app.route("/admin")
@login_required
def admin():
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) AS count FROM Users").fetchone()["count"]
    total_predictions = conn.execute("SELECT COUNT(*) AS count FROM WastePredictions").fetchone()["count"]
    avg_carbon = conn.execute("SELECT AVG(carbon_footprint) AS avg FROM WastePredictions").fetchone()["avg"] or 0
    distribution = conn.execute(
        "SELECT waste_level, COUNT(*) AS count FROM WastePredictions GROUP BY waste_level"
    ).fetchall()
    high_trends = conn.execute(
        "SELECT prediction_date, probability_high FROM WastePredictions ORDER BY id DESC LIMIT 7"
    ).fetchall()
    conn.close()
    return render_template(
        "admin.html",
        user=current_user(),
        total_users=total_users,
        total_predictions=total_predictions,
        avg_carbon=round(avg_carbon, 2),
        distribution=[dict(row) for row in distribution],
        high_trends=[dict(row) for row in high_trends],
    )


@app.post("/predict")
@login_required
def predict():
    payload = request.get_json() or {}
    result = make_prediction(payload)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ConsumptionData
        (user_id, plastic_usage, food_delivery_frequency, shopping_frequency, recycling_habits, reusable_item_usage, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            payload.get("plastic_usage", 0),
            payload.get("food_delivery_frequency", 0),
            payload.get("shopping_frequency", 0),
            payload.get("recycling_habits", 0),
            payload.get("reusable_item_usage", 0),
            now,
        ),
    )
    consumption_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO WastePredictions
        (user_id, consumption_id, waste_level, waste_score, carbon_footprint, monthly_waste_estimate,
         probability_low, probability_medium, probability_high, prediction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            consumption_id,
            result["waste_level"],
            result["waste_score"],
            result["carbon_footprint"],
            result["monthly_waste_estimate"],
            result["probability_low"],
            result["probability_medium"],
            result["probability_high"],
            now,
        ),
    )
    for text, category in result["recommendations"]:
        cursor.execute(
            "INSERT INTO Recommendations (user_id, recommendation_text, category, created_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], text, category, now),
        )
    conn.commit()
    conn.close()
    return jsonify(result)


@app.get("/api/admin-stats")
@login_required
def admin_stats():
    conn = get_db()
    rows = conn.execute("SELECT waste_level, COUNT(*) AS count FROM WastePredictions GROUP BY waste_level").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    train_model()
    app.run(debug=True)
