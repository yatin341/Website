
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



BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


NESTED_DIR = BASE_DIR / "lord-krishna-boutique"
PROJECT_DIR = NESTED_DIR if (NESTED_DIR / "templates").is_dir() else BASE_DIR

app = Flask(
    __name__,
    template_folder=str(PROJECT_DIR / "templates"),
    static_folder=str(PROJECT_DIR / "static"),
)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    app.secret_key = "dev-only-change-this-secret"
    app.logger.warning(
        "SECRET_KEY is not set. Configure a secure key in your .env file."
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
    """Create the bookings table and required compatibility columns."""
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
                ADD COLUMN created_at TIMESTAMP NULL
                DEFAULT CURRENT_TIMESTAMP
            """)

        conn.commit()
        app.logger.info("MySQL database initialized successfully.")

    finally:
        conn.close()



@app.route("/")
def home():
    return render_template(
        "index.html",
        admin_phone=os.getenv("ADMIN_PHONE", ""),
        admin_email=os.getenv("ADMIN_EMAIL", ""),
        today=date.today().isoformat(),
        current_year=date.today().year,
    )


@app.route("/book", methods=["POST"])
def book():
    # Read form values
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    booking_date = request.form.get("booking_date", "").strip()
    message = request.form.get("message", "").strip()

    # Validate name, phone, service and message using main.py
    try:
        is_valid, error_message = validate_booking(
            name, phone, service, message
        )
    except Exception:
        app.logger.exception("Booking validation failed.")
        flash("We couldn't validate your request. Please try again.", "error")
        return redirect(url_for("home") + "#booking")

    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("home") + "#booking")

    # Require a valid appointment date
    if not booking_date:
        flash("Please select your preferred appointment date.", "error")
        return redirect(url_for("home") + "#booking")

    try:
        selected_date = date.fromisoformat(booking_date)
    except ValueError:
        flash("Please select a valid appointment date.", "error")
        return redirect(url_for("home") + "#booking")

    if selected_date < date.today():
        flash("Please select today or a future date.", "error")
        return redirect(url_for("home") + "#booking")

    # Calculate service price
    try:
        price = calculate_price(service)
    except Exception:
        app.logger.exception("Could not calculate booking price.")
        flash("We couldn't process this service. Please contact us.", "error")
        return redirect(url_for("home") + "#booking")

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
            selected_date,
            message or None,
            price,
        ))

        conn.commit()

        # Show success only after MySQL confirms the save
        flash(
            "Booking request submitted successfully! "
            "Thank you for choosing Lord Krishna Boutique. "
            "We will contact you to confirm your appointment.",
            "success",
        )

    except mysql.connector.Error:
        if conn is not None:
            try:
                conn.rollback()
            except mysql.connector.Error:
                app.logger.exception("Database rollback failed.")

        app.logger.exception("Could not save the booking.")

        flash(
            "We couldn't save your booking. Please check your connection "
            "or try again later.",
            "error",
        )

    finally:
        if conn is not None:
            try:
                conn.close()
            except mysql.connector.Error:
                app.logger.exception("Could not close the database connection.")

    # Return to the booking area so the message is visible
    return redirect(url_for("home") + "#booking")




@app.route("/healthz")
def health_check():
    return {"status": "ok"}



if __name__ == "__main__":
    try:
        init_db()
    except mysql.connector.Error:
        app.logger.exception(
            "Database initialization failed. Check your .env settings and "
            "ensure MySQL is running."
        )
        raise

    app.run(debug=True)
