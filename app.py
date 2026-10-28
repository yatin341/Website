import os
from pathlib import Path
from datetime import date

import mysql.connector
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from main import validate_booking, calculate_price

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(
    __name__,
    template_folder="lord-krishna-boutique/templates",
    static_folder="lord-krishna-boutique/static",
)

app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-this-secret")

@app.route("/")
def home():
    return render_template(
        "index.html",
        admin_phone=os.getenv("ADMIN_PHONE", ""),
        admin_email=os.getenv("ADMIN_EMAIL", ""),
        today=date.today().isoformat(),
        current_year=date.today().year,
    )

def get_db_connection():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "lord_krishna_boutique"),
    )


def init_db():
    """Create the bookings table if it does not exist."""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(150) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                service VARCHAR(150) NOT NULL,
                preferred_date DATE NULL,
                message TEXT NULL,
                price INT NOT NULL DEFAULT 0,
                status VARCHAR(30) NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Keep compatibility with an older MySQL bookings table.
        cursor.execute("SHOW COLUMNS FROM bookings")
        columns = {row[0] for row in cursor.fetchall()}

        if "price" not in columns:
            cursor.execute("""
                ALTER TABLE bookings
                ADD COLUMN price INT NOT NULL DEFAULT 0
            """)

        if "created_at" not in columns:
            cursor.execute("""
                ALTER TABLE bookings
                ADD COLUMN created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            """)

        conn.commit()
        print("MySQL database initialized successfully!")

    finally:
        conn.close()



@app.route("/book", methods=["POST"])
def book():
    # Read values from the existing HTML form.
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    booking_date = request.form.get("booking_date", "").strip()
    message = request.form.get("message", "").strip()

    # Validate the booking using main.py.
    is_valid, error_message = validate_booking(
        name, phone, service, message
    )

    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("home"))

    # Validate the optional booking date.
    if booking_date:
        try:
            selected_date = date.fromisoformat(booking_date)

            if selected_date < date.today():
                flash("Please select today or a future date.", "error")
                return redirect(url_for("home"))

        except ValueError:
            flash("Please select a valid booking date.", "error")
            return redirect(url_for("home"))

    price = calculate_price(service)
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookings (
                customer_name,
                phone,
                service,
                preferred_date,
                message,
                price
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            name,
            phone,
            service,
            booking_date or None,
            message or None,
            price,
        ))

        conn.commit()

        flash(
            "Your booking request was submitted successfully!",
            "success",
        )

    except mysql.connector.Error:
        if conn is not None:
            conn.rollback()

        app.logger.exception("Could not save the booking.")
        flash(
            "We couldn't save your booking. Please try again.",
            "error",
        )

    finally:
        if conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for("home"))


@app.route("/healthz")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)