from flask import render_template, request, redirect, url_for, session, flash
from app import app
from app.models.Schedule import Schedule 
from .decorators import login_required 
from bson.objectid import ObjectId

@app.route('/set_schedule', methods=['GET', 'POST'])
@login_required
def set_schedule():
    # Ensure the logged-in user is a doctor
    if session["user_type"] != "doctor":
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard'))

    if request.method == 'POST':
        doctor_id = session["user_id"]
        days = request.form.getlist("days")  # Get list of selected days
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        # Store schedule in the database
        schedule_data = {
            "doctor_id": ObjectId(doctor_id),
            "days": days,
            "start_time": start_time,
            "end_time": end_time
        }
        Schedule.create(schedule_data)
        flash("Schedule set successfully!", "success")
        return redirect(url_for('doctor_dashboard'))

    return render_template('doctors/set_schedule.html')
@app.route('/view_schedule')
@login_required
def view_schedule():
    # Ensure the logged-in user is a doctor
    if session["user_type"] != "doctor":
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard'))

    doctor_id = session["user_id"]
    schedules = Schedule.get_by_doctor_id(ObjectId(doctor_id))
    
    # Select the first schedule if multiple are returned
    schedule = schedules[0] if schedules else None
    
    return render_template('doctors/view_schedule.html', schedule=schedule)

@app.route('/update_schedule', methods=['GET', 'POST'])
@login_required
def update_schedule():
    # Ensure the logged-in user is a doctor
    if session["user_type"] != "doctor":
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard'))

    doctor_id = session["user_id"]
    schedule = Schedule.get_by_doctor_id(ObjectId(doctor_id))

    if request.method == 'POST':
        days = request.form.getlist("days")  # Get list of selected days
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        # Update schedule in the database
        updated_data = {
            "days": days,
            "start_time": start_time,
            "end_time": end_time
        }
        
        # Use the update method from the Schedule model
        Schedule.update(ObjectId(doctor_id), updated_data)
        flash("Schedule updated successfully!", "success")
        return redirect(url_for('doctor_dashboard'))

    return render_template('doctors/update_schedule.html', schedule=schedule)
