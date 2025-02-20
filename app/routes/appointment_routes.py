from flask import render_template, request, redirect, url_for, session, flash
from app import app
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient 
from app.models.prescription import Prescription
from app.models.medication import Medication
from app.models.Schedule import Schedule
from .decorators import login_required
import logging
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app.models.payment import Payment
from flask import jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def generate_slots(start_time, end_time):
    from datetime import datetime, timedelta
    
    time_format = "%H:%M"
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)
    
    slots = []
    while start < end:
        slots.append(start.strftime(time_format))
        start += timedelta(minutes=15)
    
    return slots


@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if session["user_type"] != "patient":
        flash("Unauthorized access.", "error")
        return redirect(url_for('patient_dashboard'))

    doctor_id = request.form.get("doctor_id") if request.method == 'POST' else None
    date = request.form.get("date") if request.method == 'POST' else None
    doctors = Doctor.get_all_doctors()

    # Fetch the doctor's schedule and available slots
    schedule = Schedule.get_by_doctor_id(ObjectId(doctor_id)) if doctor_id else None
    if schedule:
        all_slots = generate_slots(schedule[0]['start_time'], schedule[0]['end_time'])
        daily_appointments = Appointment.get_daily_appointments(doctor_id, date)
        booked_slots = [appointment["time_slot"] for appointment in daily_appointments]
        available_slots = list(set(all_slots) - set(booked_slots))
    else:
        available_slots = []

    if request.method == 'POST':
        time_slot = request.form.get("time_slot")
        end_time = (datetime.strptime(time_slot, "%H:%M") + timedelta(minutes=15)).strftime("%H:%M")
        full_time_slot = f"{time_slot} - {end_time}"  # this is the complete time range
        payment_method = request.form.get("payment_method")
        amount = request.form.get("amount")  
        day_of_week = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        if day_of_week not in schedule[0]['days']:
            flash(f"The doctor is not available on {day_of_week}.", "error")
            return render_template('appointments/book_appointment.html', doctors=doctors, available_slots=available_slots)
        existing_appointment = Appointment.get_by_doctor_date_time(doctor_id, date, full_time_slot)
        print("line 66 ----",doctor_id, date, full_time_slot)
        print("line 67 ----",existing_appointment)
        if existing_appointment:
            flash("The selected time slot has just been booked by someone else. Please choose a different slot.", "error")
            return render_template('appointments/book_appointment.html', doctors=doctors, available_slots=available_slots)

        # Create the appointment with status "Pending"
        appointment_data = {
            "doctor_id": doctor_id,
            "patient_id": session["user_id"],
            "date": date,
            "time_slot": full_time_slot,  # store the complete time range
            "status": "Pending"  # initial status
        }
        created_appointment = Appointment.create(appointment_data)
        if payment_method in ["credit_card", "debit_card", "checking_account"]:
            name_on_card = request.form.get("name_on_card")
            card_number = request.form.get("card_number")
            expiry_date = request.form.get("expiry_date")
            cvv = request.form.get("cvv")     
            payment_data = {
                "name_on_card": name_on_card,
                "payment_method": payment_method,
                "card_number": card_number,
                "expiry_date": expiry_date,
                "cvv": cvv,
                "amount": amount, 
                "day_of_week": day_of_week,
                "time": datetime.now().strftime("%H:%M"),
                "status": "Paid",
                "appointment_id": appointment_data['_id']
            }
            change_status_appointment = Appointment.update(appointment_data['_id'], {"status": "Paid"})
        else:
            payment_data = {
                "payment_method": payment_method,
                "amount": amount, 
                "day_of_week": day_of_week,
                "time": datetime.now().strftime("%H:%M"),
                "status": "Not Paid",
                "appointment_id": appointment_data['_id']
            }
            change_status_appointment = Appointment.update(appointment_data['_id'], {"status": "Pending"})
            
        created_payment_data = Payment.create(payment_data)
        
        if created_appointment:
            flash("Appointment booked successfully! Status is pending.", "success")
        else:
            flash("There was a problem booking the appointment.", "error")

        if created_payment_data:
            flash("Payment details saved successfully!", "success")
        else:
            flash("There was a problem saving the payment details.", "error")

        if change_status_appointment:
            flash("Appointment status changed successfully!", "success")
        else:
            flash("There was a problem changing the appointment status.", "error")

        return redirect(url_for('view_patient_appointments'))

    return render_template('appointments/book_appointment.html', doctors=doctors, available_slots=available_slots)

@app.route('/edit_patient_appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_patient_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('patient_dashboard'))

    if session["user_type"] != "patient" or str(appointment['patient_id']) != session["user_id"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for('view_patient_appointments'))

    doctors = Doctor.get_all_doctors()
    doctor_id = request.form.get("doctor_id") if request.method == 'POST' else appointment['doctor_id']
    date = request.form.get("date") if request.method == 'POST' else appointment['date']
    selected_slot = appointment['time_slot']

    # If it's a GET request, fetch available slots for the doctor and date
    if request.method == 'GET':
        # You will need to extract the start time from the selected_slot to get available slots
        start_time = selected_slot.split(" - ")[0]
        end_time = selected_slot.split(" - ")[1]
        all_slots = generate_slots(start_time, end_time)
        available_slots = all_slots

    if request.method == 'POST':
        # For POST, you would validate and update all the appointment details
        time_slot = request.form.get("time_slot")
        end_time = (datetime.strptime(time_slot, "%H:%M") + timedelta(minutes=15)).strftime("%H:%M")
        full_time_slot = f"{time_slot} - {end_time}"  # This is the complete time range
        
        # If the appointment time slot has changed, check if the new slot is available
        if full_time_slot != selected_slot:
            daily_appointments = Appointment.get_daily_appointments(doctor_id, date)
            booked_slots = [appointment["time_slot"] for appointment in daily_appointments]
            if full_time_slot in booked_slots:
                flash("The selected time slot is no longer available.", "error")
                return render_template('appointments/update_patient_appointment.html', 
                                       doctors=doctors, 
                                       appointment=appointment, 
                                       available_slots=available_slots)
        

        # Update the appointment
        updated_data = {
            "doctor_id": doctor_id,
            "date": date,
            "time_slot": full_time_slot
        }
        Appointment.update(appointment_id, updated_data)
        flash("Appointment updated successfully!", "success")
        return redirect(url_for('view_patient_appointments'))

    return render_template('appointments/update_patient_appointment.html', 
                           doctors=doctors, 
                           appointment=appointment, 
                           available_slots=available_slots)

@app.route('/cancel_patient_appointment/<appointment_id>', methods=['POST'])
@login_required
def cancel_patient_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('patient_dashboard'))

    Appointment.delete(appointment_id)
    flash("Appointment cancelled successfully!", "success")
    return redirect(url_for('view_patient_appointments'))



@app.route('/view_patient_appointments')
@login_required
def view_patient_appointments(): 
    appointments = Appointment.get_appointments_by_user(session["user_id"])
    print("line 198 ----",appointments)

    for appointment in appointments:
        prescription = Prescription.get_by_appointment(appointment['_id']) if appointment else None
        medication = Medication.get_by_prescription(prescription['_id']) if prescription else None
        appointment['prescription'] = prescription if prescription else None
        appointment['medication'] = medication[0] if medication else None

    return render_template('appointments/view_appointments.html', appointments=appointments)

# DOCTOR ROUTES
@app.route('/doctor_view_appointments', methods=['GET', 'POST'])
@login_required
def view_doctor_appointments():     
    # Ensure the logged-in user is a doctor
    if session["user_type"] != "doctor":
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard')) 
    appointments = Appointment.get_appointments_by_doctor(session["user_id"])
    return render_template('appointments/doctor_view_appointments.html', appointments=appointments)


@app.route('/edit_doctor_appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('doctor_dashboard'))

    # Ensure the logged-in doctor is associated with the appointment
    if session["user_type"] != "doctor" or str(appointment['doctor_id']) != session["user_id"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard'))

    patient = Patient.get_patient_by_id(appointment['patient_id'])
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('doctor_dashboard'))

    if request.method == 'POST':
        # Get status from the form
        status = request.form.get("status")

        # Update the appointment with the new status
        updated_data = {
            "status": status
        }
        Appointment.update(appointment_id, updated_data)
        flash("Appointment status updated successfully!", "success")
        return redirect(url_for('view_doctor_appointments'))
    return render_template('appointments/edit_doctor_appointment.html', appointment=appointment, patient=patient)

    # GET request: render the template with the current status
    return render_template('appointments/edit_doctor_appointment.html', appointment=appointment, patient=patient)

@app.route('/cancel_doctor_appointment/<appointment_id>', methods=['POST'])
@login_required
def cancel_doctor_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('doctor_dashboard'))

    # Ensure the logged-in doctor is associated with the appointment
    if str(appointment['doctor_id']) != session["user_id"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for('doctor_dashboard'))

    Appointment.delete(appointment_id)
    flash("Appointment cancelled successfully!", "success")
    return redirect(url_for('view_doctor_appointments'))


@app.route('/get_available_slots', methods=['POST'])
@login_required
def get_available_slots():
    doctor_id = request.form.get("doctor_id")
    date = request.form.get("date")

    # Fetch the doctor's schedule
    schedule = Schedule.get_by_doctor_id(ObjectId(doctor_id))
    if not schedule:
        return jsonify(error="Doctor's schedule not available.", available_slots=[])

    all_slots = generate_slots(schedule[0]['start_time'], schedule[0]['end_time'])
    daily_appointments = Appointment.get_daily_appointments(doctor_id, date)
    booked_slots = [appointment["time_slot"] for appointment in daily_appointments]
    available_slots = list(set(all_slots) - set(booked_slots))

    # Convert available slots to a user-friendly format
    user_friendly_slots = ["{} - {}".format(slot, (datetime.strptime(slot, "%H:%M") + timedelta(minutes=15)).strftime("%H:%M")) for slot in available_slots]
    available_slots = list(set(all_slots) - set(booked_slots))

    return jsonify(available_slots=user_friendly_slots)
