Lord Krishna Boutique - Booking System

A Flask-based web application for managing customer booking requests for boutique services. The application allows users to select a service (e.g., Suit Stitching, Bridal Wear), choose a preferred date, and submit a booking request, which is securely saved to a MySQL database.

Features

Service Selection: Customers can choose from various predefined services (Suit Stitching, Lehenga Stitching, Bridal Wear, etc.).

Dynamic Pricing: Calculates estimated prices based on the selected service.

Validation Engine: Built-in backend validation for names, 10-digit phone numbers, and service availability.

MySQL Integration: Automatically creates and initializes the bookings table upon startup if it doesn't exist.

Secure Configuration: Uses .env files to protect database credentials and secret keys.

Prerequisites

Before you begin, ensure you have the following installed on your machine:

Python 3.7+

MySQL Server

Installation & Setup

1. Clone or Download the Repository
Ensure all project files (app.py, main.py, .env, requirements.txt) and folders (lord-krishna-boutique/templates, lord-krishna-boutique/static) are together in your project directory.

2. Install Dependencies
Open your terminal/command prompt, navigate to your project folder, and install the required Python packages:

pip install -r requirements.txt


3. Database Setup
Log into your MySQL server and create the database:

CREATE DATABASE lord_krishna_boutique;


(Note: The application's init_db() function will automatically create the necessary bookings table for you when you run the app).

4. Environment Variables Setup
Create or update the .env file in the root directory of your project with the following structure. Replace the values with your actual MySQL credentials:

SECRET_KEY=your_secure_random_secret_key_here
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=lord_krishna_boutique
ADMIN_PHONE=6280715453
ADMIN_EMAI=yatinjangra97@gmail.com


Running the Application

Once your database is running and your .env is configured, start the application by running:

python app.py


The server will start on http://127.0.0.1:5000/. You should see MySQL database initialized successfully! in your console.

Project Structure

app.py: The main Flask application containing the routes, database connection logic, and table initialization.

main.py: The business logic file containing service definitions, pricing arrays, and form validation rules.

.env: Environment configuration file (keep this private and do not commit to public repositories).

requirements.txt: List of Python dependencies.

lord-krishna-boutique/templates/: Folder containing HTML templates (like index.html).

lord-krishna-boutique/static/: Folder containing static assets (CSS, JS, images).