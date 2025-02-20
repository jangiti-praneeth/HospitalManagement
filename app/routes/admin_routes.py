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
from app.models.feedback import Feedback
from app.models.payment import Payment
from flask import jsonify



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/view_admin_appointments', methods=['GET', 'POST'])
@login_required
def view_admin_appointments():   
    print("=============Inside view_admin_appointments=============")  
    appointments = Appointment.get_all_appointments()
    for appointment in appointments:
        appointment['doctor_name'] = Doctor.get_doctor_name_by_id(appointment['doctor_id'])
        appointment['patient_name'] = Patient.get_patient_name_by_id(appointment['patient_id'])
    # appointments = [{'patient_name': 'Test Patient', 'doctor_name': 'Test Doctor', 'date': '2023-01-01', 'time_slot': '10:00', 'status': 'Scheduled'}]
    return render_template('admin/view_admin_appointments.html', appointments=appointments)



@app.route('/view_all_doctors', methods=['GET', 'POST'])
@login_required
def view_all_doctors():   
    print("=============Inside view_all_doctors=============")  
    doctors = Doctor.get_all_doctors()
    # doctors = [{'name': 'Test Doctor', 'email': 'testdoctor@gmail', 'speciality': 'Test Speciality', 'phone': '1234567890'}]
    return render_template('admin/view_all_doctors.html', doctors=doctors)


@app.route('/view_all_patients', methods=['GET', 'POST'])
@login_required
def view_all_patients():   
    print("=============Inside view_all_patients=============")  
    patients = Patient.get_all_patients()
    # patients = [{'name': 'Test Patient', 'email': 'testpatient@gmail', 'phone': '1234567890'}]
    return render_template('admin/view_all_patients.html', patients=patients)


@app.route('/view_all_payments', methods=['GET', 'POST'])
@login_required
def view_all_payments():   
    print("=============Inside view_all_payments=============")  
    payments = Payment.get_all_payments()
    print("total number of payments====", len(payments))
    # payments = [{'patient_name': 'Test Patient', 'doctor_name': 'Test Doctor', 'amount': '100', 'date': '2023-01-01'}]
    return render_template('admin/view_all_payments.html', payments=payments)

# =================== generate slots ===================
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

# ===================Book Appointment===================
def calculate_available_slots(doctor_id, date):
    schedule = Schedule.get_by_doctor_id(ObjectId(doctor_id))
    if not schedule:
        return []

    all_slots = generate_slots(schedule[0]['start_time'], schedule[0]['end_time'])
    daily_appointments = Appointment.get_daily_appointments(doctor_id, date)
    booked_slots = [appointment["time_slot"] for appointment in daily_appointments]
    return list(set(all_slots) - set(booked_slots))

def create_payment_data(form, appointment_id):
    payment_method = form.get("payment_method")
    payment_status = "Paid" if payment_method in ["credit_card", "debit_card", "checking_account"] else "Not Paid"
    
    payment_data = {
        "payment_method": payment_method,
        "amount": form.get("amount"),
        "day_of_week": datetime.strptime(form.get("date"), "%Y-%m-%d").strftime("%A"),
        "time": datetime.now().strftime("%H:%M"),
        "status": payment_status,
        "appointment_id": appointment_id
    }

    if payment_status == "Paid":
        payment_data.update({
            "card_number": form.get("card_number"),
            "expiry_date": form.get("expiry_date"),
            "cvv": form.get("cvv")
        })

    return payment_data

@app.route('/admin_book_appointment', methods=['GET', 'POST'])
@login_required
def admin_book_appointment():
    doctors = Doctor.get_all_doctors()
    doctor_id, date, available_slots = None, None, []

    if request.method == 'POST':
        doctor_id = request.form.get("doctor_id")
        date = request.form.get("date")
        available_slots = calculate_available_slots(doctor_id, date)
        patient_type = request.form.get("patient_type")
        time_slot = request.form.get("time_slot")
        full_time_slot = calculate_full_time_slot(time_slot)

        if patient_type == "new_patient":
            patient_name = request.form.get("new_patient_name")
            patient_email = request.form.get("new_patient_email")
            # Create a new patient record here
            patient_id = create_new_patient(patient_name, patient_email)
            # patient_id = new_patient_id 
        else:
            patient_email = request.form.get("registered_patient_email")
            print("line 132", patient_email)
            registered_patient = Patient.get_patient_by_email(patient_email)
            print("line 134", registered_patient)
            patient_id = registered_patient['_id'] if registered_patient else None
            print("line 136", patient_id)
        if not patient_id:
            flash("No registered user found with this email.", "error")
            return redirect(url_for('admin_book_appointment'))

        if Appointment.get_by_doctor_date_time(doctor_id, date, full_time_slot):
            flash("Selected time slot is unavailable.", "error")
        else:
            appointment_data = create_appointment_data(request.form, full_time_slot, patient_id)
            print("line 137", appointment_data)
            payment_data = create_payment_data(request.form, appointment_data)
            print("line 139", payment_data)
            handle_appointment_creation(appointment_data, payment_data)
            return redirect(url_for('view_admin_appointments'))
    else:
        doctor_id = request.args.get("doctor_id")
        date = request.args.get("date")
        if doctor_id and date:
            available_slots = calculate_available_slots(doctor_id, date)

    return render_template('admin/book_admin_appointment.html', doctors=doctors, available_slots=available_slots)

def calculate_full_time_slot(time_slot):
    end_time = (datetime.strptime(time_slot, "%H:%M") + timedelta(minutes=15)).strftime("%H:%M")
    return f"{time_slot} - {end_time}"

def create_appointment_data(form, full_time_slot, new_patient_id):
    return {
        "doctor_id": form.get("doctor_id"),
        "patient_id": new_patient_id,  # Adjust based on your admin booking logic
        "date": form.get("date"),
        "time_slot": full_time_slot,
        "status": "Pending"
    }

def handle_appointment_creation(appointment_data, payment_data):
    created_appointment = Appointment.create(appointment_data)
    appointment_id = created_appointment.inserted_id
    payment_data = create_payment_data(request.form, appointment_id)
    created_payment_data = Payment.create(payment_data)
    update_status = Appointment.update(appointment_data['_id'], {"status": payment_data["status"]})

    flash_messages_based_on_creation(created_appointment, created_payment_data, update_status)

def flash_messages_based_on_creation(appointment, payment, status_update):
    flash("Appointment booked successfully!" if appointment else "Error booking appointment.", "success" if appointment else "error")
    flash("Payment details saved." if payment else "Error saving payment details.", "success" if payment else "error")
    flash("Appointment status updated." if status_update else "Error updating status.", "success" if status_update else "error")


def create_new_patient(name, email):
    insert_result = Patient.create(
        {
        "name": name,
        "dob": "",
        "sex": "",
        "contactInfo": {
                    "email": email,
                    "phone": "",
                    "address": ""
                },
        "password": "",
        })
    if insert_result.acknowledged:
        new_patient_id = insert_result.inserted_id
        print(f"New patient created with ID: {new_patient_id}")
        return new_patient_id
    else:
        # Handle the error case where the insert was not acknowledged
        print("Failed to create new patient.")
        return None
    
    

@app.route('/edit_admin_appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_admin_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('admin_dashboard'))

    patient = Patient.get_patient_by_id(appointment['patient_id'])
    if not patient:
        flash("Patient not found.", "error")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        # Get status from the form
        status = request.form.get("status")

        # Update the appointment with the new status
        updated_data = {
            "status": status
        }
        Appointment.update(appointment_id, updated_data)
        flash("Appointment status updated successfully!", "success")
        return redirect(url_for('view_admin_appointments'))
    return render_template('admin/edit_admin_appointment.html', appointment=appointment, patient=patient)

    # GET request: render the template with the current status

@app.route('/cancel_admin_appointment/<appointment_id>', methods=['POST'])
@login_required
def cancel_admin_appointment(appointment_id):
    appointment = Appointment.get_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "error")
        return redirect(url_for('admin_dashboard'))

    Appointment.delete(appointment_id)
    flash("Appointment cancelled successfully!", "success")
    return redirect(url_for('view_admin_appointments'))



@app.route('/view_patient_on_appointment_admin/<appointment_id>', methods=['GET', 'POST'])
@login_required
def view_patient_on_appointment_admin(appointment_id): 
    patient_data = Patient.get_by_appointment(ObjectId(appointment_id)) 
    patient = {
    "name": patient_data.get("name", "Not available"),
    "dob": patient_data.get("dob", "Not available"),
    "sex": patient_data.get("sex", "Not available"),
    "contactInfo": {
        "email": patient_data.get("contactInfo.email", "Not available"),
        "phone": patient_data.get("contactInfo.phone", "Not available"),
        "address": patient_data.get("contactInfo.address", "Not available")
    }
    }

    if not patient:
        flash("No patient found for this appointment.", "error") 
        return redirect(url_for('admin_dashboard'))
    
    return render_template(
        'prescription/view_patient_on_appointment_admin.html',
        appointment_id=appointment_id,
        patient=patient
    )



# ===================feedbacks===================
@app.route('/view_all_feedbacks', methods=['GET'])
@login_required
def view_all_feedbacks():
    feedbacks = Feedback.get_all_feedbacks()  # This method should return all feedbacks
    feedbacks = list(feedbacks)
    print("feedbacks=======================", feedbacks)
    for feedback in feedbacks:
        appointment = Appointment.get_by_id(feedback['appointment_id'])
        print("appointment=======================", appointment)
        if appointment:
            feedback['doctor_name'] = Doctor.get_doctor_name_by_id(appointment['doctor_id'])
            feedback['patient_name'] = Patient.get_patient_name_by_id(appointment['patient_id'])
            feedback['appointment_date'] = appointment['date']
            feedback['appointment_time'] = appointment['time_slot']
            print("line 294n=======================", feedback['doctor_name'], feedback['patient_name'], feedback['appointment_date'], feedback['appointment_time'])
        else:
            # Handle the case where appointment is not found
            feedback['doctor_name'] = 'Unknown'
            feedback['patient_name'] = 'Unknown'
            feedback['appointment_date'] = 'Unknown'
            feedback['appointment_time'] = 'Unknown'
            print("line 301=======================", feedback['doctor_name'], feedback['patient_name'], feedback['appointment_date'], feedback['appointment_time'])
    print("Feedbacks to be rendered:", feedbacks)
    return render_template('admin/view_all_feedbacks.html', feedbacks=feedbacks)


# ===================medications===================
@app.route('/view_all_medications', methods=['GET'])
@login_required
def view_all_medications():
    medications = Medication.get_all_medications()  # Fetch all medications
    medication_list = list(medications)

    for medication in medication_list:
        # Fetch prescription details
        prescription_id = medication['prescription']
        prescription = Prescription.get_by_id(prescription_id)
        
        if prescription:
            # Fetch appointment details
            appointment_id = prescription['appointment']
            appointment = Appointment.get_by_id(appointment_id)

            if appointment:
                medication['doctor_name'] = Doctor.get_doctor_name_by_id(appointment['doctor_id'])
                medication['patient_name'] = Patient.get_patient_name_by_id(appointment['patient_id'])
                medication['appointment_datetime'] = f"{appointment['date']} {appointment['time_slot']}"
            else:
                medication['doctor_name'] = 'Unknown'
                medication['patient_name'] = 'Unknown'
                medication['appointment_datetime'] = 'Unknown'

            medication['prescription_text'] = prescription['prescription_text']
        else:
            medication['doctor_name'] = 'Unknown'
            medication['patient_name'] = 'Unknown'
            medication['appointment_datetime'] = 'Unknown'
            medication['prescription_text'] = 'Unknown'

    return render_template('admin/view_all_medications.html', medications=medication_list)
