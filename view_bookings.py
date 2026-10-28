import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings")

    bookings = cursor.fetchall()

    if bookings:
        print("\n===== CUSTOMER BOOKINGS =====\n")

        for number, booking in enumerate(bookings, start=1):
            print(f"Booking #{number}")
            for key, value in booking.items():
                print(f"{key}: {value}")
            print("-" * 40)
    else:
        print("No bookings found in the database.")

    cursor.close()
    connection.close()

except mysql.connector.Error as error:
    print("Database error:", error)