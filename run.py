from app import app
from app.routes import auth_routes, profile_routes, default_routes, appointment_routes, schedule_routes, prescription_routes, feedback_routes, payment_routes, admin_routes


if __name__ == "__main__":
    app.run(debug=False)
