from app.models.medication import Medication
from flask import render_template, request, redirect, url_for, session
from app import app 
from .decorators import login_required
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from bson import ObjectId, errors


@app.route('/view_patient_on_appointment2/<appointment_id>', methods=['GET', 'POST'])
@login_required
def view_patient_on_appointment(appointment_id): 
    patient = Patient.get_by_appointment(ObjectId(appointment_id)) 
    if not patient:
        flash("No patient found for this appointment.", "error")
        print("No patient found for this appointment.")
        return redirect(url_for('doctor_dashboard'))
        
    prescription = Prescription.get_by_appointment(appointment_id)
    
    if request.method == 'POST':
        prescription_text = request.form.get("prescription_text")
        medication = request.form.get("medication")
        prescription_data = {
            "appointment": appointment_id,
            "prescription_text": prescription_text,
            "medication": medication
        }
        
        if prescription:
            # Update existing prescription if one exists
            Prescription.update(prescription["_id"], prescription_data)
            flash("Prescription updated successfully!", "success")
        else:
            # Or create a new prescription
            Prescription.create(prescription_data)
            flash("Prescription created successfully!", "success")
        return redirect(url_for('dashboard'))  # Or wherever the doctor should be redirected after prescribing
    # Pass patient and prescription to the template
    return render_template('prescription/view_patient_on_appointment.html', patient=patient, prescription=prescription, appointment_id=appointment_id)


# @app.route('/submit_prescription/<appointment_id>')
# @login_required
# def submit_prescription(appointment_id):
#     patient =Patient.get_by_appointment(ObjectId(appointment_id))
#     prescription = Prescription.get_by_appointment(appointment_id)
#     # Render the template with the required context variables
#     return render_template(
#         'prescription/view_patient_on_appointment.html',
#         appointment_id=appointment_id,
#         patient=patient,
#         prescription=prescription
#     )

@app.route('/save_prescription/<appointment_id>', methods=['POST'])
@login_required
def save_prescription(appointment_id):
    print("the appointment id is: ", appointment_id)
    prescription_text = request.form.get("prescription_text")
    print(f"Saving prescription: {prescription_text}")
    # Check if a prescription for this appointment already existsE
    prescription = Prescription.get_by_appointment(appointment_id) 
    if prescription: 
        Prescription.update(prescription['_id'], {'prescription_text': prescription_text})
        flash("Prescription updated successfully!", "success")
    else: 
        new_prescription_data = {
            "appointment": ObjectId(appointment_id),
            "prescription_text": prescription_text
        }
        Prescription.create(new_prescription_data)
        flash("Prescription created successfully!", "success")
    
    # Redirect to a confirmation page or back to the form, for instance
    return redirect(url_for('submit_prescription', appointment_id=appointment_id))
