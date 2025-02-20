# app/profile_routes.py

from flask import render_template, request, redirect, url_for, session
from app import app
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.admin import Admin
from .decorators import login_required
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash

# All your profile routes go here...

# @app.route('/dashboard')
# @login_required
# def dashboard(): 
#     return render_template('users/dashboard.html')
@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if session["user_type"] != "doctor":
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    return render_template('doctors/doctor_dashboard.html')

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if session["user_type"] != "patient":
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    return render_template('patients/patient_dashboard.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if session["user_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    return render_template('admin/admin_dashboard.html')

from bson import ObjectId
@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if user_type == "doctor":
        user_model = Doctor
    elif user_type == "patient":
        user_model = Patient
    else:
        flash("Invalid user type", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Get the data from the form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")

        # Update the user's data in the database
        try:
            result = user_model.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "name": name,
                        "contactInfo.email": email,
                        "contactInfo.phone": phone,
                        "contactInfo.address": address
                    }
                }
            )

            # Check if the update was successful
            if result.modified_count == 0:
                flash("No changes were made.", "info")
            else:
                flash("Profile updated successfully!", "success")

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('update_profile'))
#  if user is doctor return doctor_dashboard else patient_dashboard
        if user_type == "doctor":
            return redirect(url_for('doctor_dashboard'))
        elif user_type == "patient":
            return redirect(url_for('patient_dashboard')) 

    else:
        # Fetch the user's current data
        user = user_model.collection.find_one({"_id": ObjectId(user_id)})
        
        # Check if user is found
        if not user:
            flash("User not found", "error")
            return redirect(url_for('dashboard'))

        return render_template('users/update_profile.html', user=user)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if user_type == "doctor":
        user_model = Doctor
    elif user_type == "patient":
        user_model = Patient
    else:
        flash("Invalid user type", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user = user_model.collection.find_one({"_id": ObjectId(user_id)})

        # Verify current password
        if not user_model.check_password(user, current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('change_password'))

        # Check if new password matches confirmation
        if new_password != confirm_password:
            flash("New password and confirmation do not match", "error")
            return redirect(url_for('change_password'))

        # Check if new password meets criteria (e.g., length)
        # if len(new_password) < 8:
        #     flash("New password should be at least 8 characters long", "error")
        #     return redirect(url_for('change_password'))

        # Update password in the database
        hashed_password = generate_password_hash(new_password)
        user_model.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password}}
        )

        flash("Password updated successfully!", "success")
        #  if user is doctor return doctor_dashboard else patient_dashboard
        if user_type == "doctor":
            return redirect(url_for('doctor_dashboard'))
        elif user_type == "patient":
            return redirect(url_for('patient_dashboard')) 

    return render_template('users/change_password.html')



# =================== Admin Routes ===================
@app.route('/update_admin_profile', methods=['GET', 'POST'])
@login_required
def update_admin_profile():
    # Ensure the logged-in user is an admin
    if session.get('user_type') != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        # Get the data from the form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        dob = request.form.get("dob")
        sex = request.form.get("sex")

        # Update the admin's data in the database
        try:
            result = Admin.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "name": name,
                        "contactInfo.email": email,
                        "contactInfo.phone": phone,
                        "contactInfo.address": address,
                        "dob": dob,
                        "sex": sex
                    }
                }
            )

            if result.modified_count == 0:
                flash("No changes were made.", "info")
            else:
                flash("Profile updated successfully!", "success")

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('update_admin_profile'))

        return redirect(url_for('admin_dashboard'))

    else:
        # Fetch the admin's current data
        admin = Admin.collection.find_one({"_id": ObjectId(user_id)})
        if not admin:
            flash("Admin not found", "error")
            return redirect(url_for('dashboard'))

        return render_template('admin/update_admin_profile.html', admin=admin)

@app.route('/change_admin_password', methods=['GET', 'POST'])
@login_required
def change_admin_password():
    # Ensure the logged-in user is an admin
    if session.get('user_type') != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        admin = Admin.collection.find_one({"_id": ObjectId(user_id)})

        # Verify current password
        if not Admin.check_password(admin, current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('change_admin_password'))

        # Check if new password matches confirmation
        if new_password != confirm_password:
            flash("New password and confirmation do not match", "error")
            return redirect(url_for('change_admin_password'))

        # Update password in the database
        hashed_password = generate_password_hash(new_password)
        Admin.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password}}
        )

        flash("Password updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/change_admin_password.html')
