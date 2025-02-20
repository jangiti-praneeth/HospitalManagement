from flask import render_template, request, redirect, url_for, session
from app import app
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#     return render_template('users/login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get("user_type")
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        print(user_type)
        print(email)
        print(password)
        user = None
        if user_type == "doctor":
            print("inside doctor")
            user = Doctor.get_by_email(email)
        elif user_type == "patient":
            print("inside patient")
            user = Patient.get_by_email(email)
        elif user_type == "admin":
            print("inside admin")
            user = Admin.get_by_email(email)

        if not user:
            return "Email not found", 404

        is_valid_password = False
        if user_type == "doctor":
            is_valid_password = Doctor.check_password(user, password)
        elif user_type == "patient":
            is_valid_password = Patient.check_password(user, password)
        elif user_type == "admin":
            is_valid_password = Admin.check_password(user, password)

        if not is_valid_password:
            return "Invalid password", 401

        session["user_id"] = str(user["_id"])
        session["user_type"] = user_type

        # Redirect to the appropriate dashboard after successful login
        if user_type == "doctor":
            return redirect(url_for('doctor_dashboard'))
        elif user_type == "patient":
            return redirect(url_for('patient_dashboard'))
        elif user_type == "admin":
            return redirect(url_for('admin_dashboard'))

    return render_template('users/login.html')

@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    try:
        if request.method == 'POST':
            email = request.form.get("email").strip()
            if Doctor.exists_by_email(email):
                return "Email already registered", 400

            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if password != confirm_password:
                return "Passwords do not match", 400

            data = {
                "first_name": request.form.get("first_name").strip(),
                "last_name": request.form.get("last_name").strip(),
                "ssn": request.form.get("ssn").strip(),
                "specialisation": request.form.get("specialisation").strip(),
                "contactInfo": {
                    "email": email,
                    "phone": request.form.get("phone").strip(),
                    "address": request.form.get("address").strip()
                },
                "password": generate_password_hash(password)
            }
            Doctor.create(data)
            return redirect(url_for('login'))

        return render_template('doctors/register_doctor.html')
    except Exception as e:
        logger.error(f"Error during doctor registration: {e}", exc_info=True)
        return "Internal Server Error", 500


@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    try:
        if request.method == 'POST':
            email = request.form.get("email").strip()
            if Patient.exists_by_email(email):
                return "Email already registered", 400

            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if password != confirm_password:
                return "Passwords do not match", 400

            data = {
                "first_name": request.form.get("first_name").strip(),
                "last_name": request.form.get("last_name").strip(),
                "ssn": request.form.get("ssn").strip(),
                "height": request.form.get("height"),
                "weight": request.form.get("weight"),
                "dob": request.form.get("dob").strip(),
                "sex": request.form.get("sex"),
                "contactInfo": {
                    "email": email,
                    "phone": request.form.get("phone").strip(),
                    "address": request.form.get("address").strip()
                },
                "password": generate_password_hash(password)
            }
            Patient.create(data)
            return redirect(url_for('login'))

        return render_template('patients/register_patient.html')
    except Exception as e:
        logger.error(f"Error during patient registration: {str(e)}")
        return "Internal Server Error", 500

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    try:
        if request.method == 'POST':
            user_type = request.form.get("user_type")
            email = request.form.get("email")

            if user_type == "doctor" and Doctor.exists_by_email(email):
                session["reset_email"] = email
                session["user_type"] = user_type
                return redirect(url_for('enter_otp'))
            elif user_type == "patient" and Patient.exists_by_email(email):
                session["reset_email"] = email
                session["user_type"] = user_type
                return redirect(url_for('enter_otp'))
            else:
                return "Email not found", 404

        return render_template('users/forgot_password.html')
    except Exception as e:
        logger.error(f"Error during forgot password process: {str(e)}")
        return "Internal Server Error", 500

@app.route('/enter_otp', methods=['GET', 'POST'])
def enter_otp():
    try:
        if request.method == 'POST':
            otp = request.form.get("otp")
            if otp == "11111":
                return redirect(url_for('reset_password'))
            else:
                return "Invalid OTP", 400

        return render_template('users/enter_otp.html')
    except Exception as e:
        logger.error(f"Error during OTP verification: {str(e)}")
        return "Internal Server Error", 500

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    try:
        if "reset_email" not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            new_password = request.form.get("new_password")
            hashed_password = generate_password_hash(new_password)

            if session["user_type"] == "doctor":
                Doctor.collection.update_one(
                    {"contactInfo.email": session["reset_email"]},
                    {"$set": {"password": hashed_password}}
                )
            elif session["user_type"] == "patient":
                Patient.collection.update_one(
                    {"contactInfo.email": session["reset_email"]},
                    {"$set": {"password": hashed_password}}
                )

            session.pop("reset_email", None)
            session.pop("user_type", None)
            return redirect(url_for('login'))

        return render_template('users/reset_password.html')
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        return "Internal Server Error", 500

@app.route('/logout')
def logout():
    try:
        session.pop('user_id', None)
        session.pop('user_type', None)
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return "Internal Server Error", 500




# register admin secret url
@app.route('/admin_secret', methods=['GET', 'POST'])
def register_admin():
    try:
        if request.method == 'POST':
            email = request.form.get("email").strip()
            if Admin.exists_by_email(email):
                return "Email already registered", 400

            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if password != confirm_password:
                return "Passwords do not match", 400

            data = {
                "first_name": request.form.get("first_name").strip(),
                "last_name": request.form.get("last_name").strip(),
                "ssn": request.form.get("ssn").strip(),
                "dob": request.form.get("dob").strip(),
                "sex": request.form.get("sex"),
                "contactInfo": {
                    "email": email,
                    "phone": request.form.get("phone").strip(),
                    "address": request.form.get("address").strip()
                },
                "password": generate_password_hash(password)
            }
            Admin.create(data)
            return redirect(url_for('login'))

        return render_template('admin/register_admin.html')
    except Exception as e:
        logger.error(f"Error during admin registration: {str(e)}")
        return "Internal Server Error", 500
