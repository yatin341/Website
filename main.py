

ALLOWED_SERVICES = {
    "Suit Stitching",
    "Lehenga Stitching",
    "Bridal Wear",
    "Dress Stitching",
    "Alterations",
    "Other",
}

# Example prices in INR. Change these to your actual prices.
SERVICE_PRICES = {
    "Suit Stitching": 1200,
    "Lehenga Stitching": 3000,
    "Bridal Wear": 10000,
    "Dress Stitching": 800,
    "Alterations": 200,
    "Other": 0,
}


def validate_booking(name, phone, service, message=""):
    """Validate customer booking information."""

    if not name:
        return False, "Please enter your name."

    if len(name) > 100:
        return False, "Your name must be 100 characters or fewer."

    if not phone.isdigit() or len(phone) != 10 or len(phone) < 10:
        return False, "Please enter a valid 10-digit phone number."

    if service not in ALLOWED_SERVICES:
        return False, "Please select a valid service."

    if len(message) > 1000:
        return False, "Your message must be 1000 characters or fewer."

    return True, "Booking details are valid."


def calculate_price(service):
    """Return the example price for a service."""

    return SERVICE_PRICES.get(service, 0)