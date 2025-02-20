#  hi index route
from flask import render_template
from app import app
from app.models.doctor import Doctor
from flask import redirect, url_for, session

@app.route('/')
def index():
    print("index route")
    # Check if user is already logged in
    if 'user_id' in session:
        # Check the user type and redirect to the appropriate dashboard
        if session["user_type"] == "doctor":
            return redirect(url_for('doctor_dashboard'))
        elif session["user_type"] == "patient":
            return redirect(url_for('patient_dashboard'))

    doctors = Doctor.get_all_doctors()  # Assuming you have this method in your Doctor model
    return render_template('index.html', doctors=doctors)
