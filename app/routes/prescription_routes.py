from app.models.prescription import Prescription
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
from app.models.medication import Medication


@app.route('/view_patient_on_appointment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def view_patient_on_appointment(appointment_id): 
    patient = Patient.get_by_appointment(ObjectId(appointment_id)) 
    if not patient:
        flash("No patient found for this appointment.", "error") 
        return redirect(url_for('doctor_dashboard'))
    prescription = Prescription.get_by_appointment(appointment_id)
    if prescription:
        medication = Medication.get_by_prescription(prescription['_id'])
        medication = medication[0] if medication else None
    else:
        medication = None

    
    if request.method == 'POST':
        prescription_text = request.form.get("prescription_text")
        medication = request.form.get("medication")
        prescription_data = {
            "appointment": appointment_id,
            "prescription_text": prescription_text
        }
        if prescription:
            # Update existing prescription if one exists
            Prescription.update(prescription["_id"], prescription_data)
            flash("Prescription updated successfully!", "success")
        else:
            # Or create a new prescription
            Prescription.create(prescription_data)
            flash("Prescription created successfully!", "success")
        return redirect(url_for('dashboard'))  
    return render_template(
        'prescription/view_patient_on_appointment.html',
        appointment_id=appointment_id,
        patient=patient,
        prescription=prescription,
        medication=medication
    )


@app.route('/submit_prescription/<appointment_id>')
@login_required 
def submit_prescription(appointment_id):
    patient = Patient.get_by_appointment(ObjectId(appointment_id))
    prescription = Prescription.get_by_appointment(appointment_id)

    medication = None
    if prescription:
        medication_list = Medication.get_by_prescription(prescription['_id'])
        if medication_list:
            medication = medication_list[0]
            

    return render_template(
        'prescription/view_patient_on_appointment.html',
        appointment_id=appointment_id,
        patient=patient,
        prescription=prescription,
        medication=medication
    )


@app.route('/submit_medication/<appointment_id>')
@login_required
def submit_medication(appointment_id):
    patient =Patient.get_by_appointment(ObjectId(appointment_id))
    prescription = Prescription.get_by_appointment(appointment_id)
    medication = Medication.get_by_prescription(prescription['_id'])
    

    # return render_template(
    #     'appointments/doctor_view_appointments.html',
    #     appointment_id=appointment_id,
    #     patient=patient,
    #     prescription=prescription,
    #     medication=medication[0]
    # )

    return redirect(url_for('view_doctor_appointments'))
@app.route('/save_prescription/<appointment_id>', methods=['POST'])
@login_required
def save_prescription(appointment_id): 
    prescription_text = request.form.get("prescription_text") 
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


@app.route('/save_medication/<appointment_id>', methods=['POST'])
@login_required
def save_medication(appointment_id): 
    medication_texts = request.form.getlist("medication_text[]")
    dosages = request.form.getlist("dosage[]") 
    prescription = Prescription.get_by_appointment(appointment_id)

    # Iterate through each medication and dosage pair
    for medication_text, dosage in zip(medication_texts, dosages):
        if medication_text and dosage:  # Check if both fields are filled
            new_medication_data = { 
                "prescription": ObjectId(prescription['_id']),
                "dosage": dosage,
                "medication_text": medication_text
            }
            Medication.create(new_medication_data)
    
    flash("Medication(s) updated successfully!", "success")
    return redirect(url_for('submit_medication', appointment_id=appointment_id))

