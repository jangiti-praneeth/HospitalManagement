from flask import render_template, request, redirect, url_for, session
from app import app
from app.models.feedback import Feedback 
from .decorators import login_required
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/give_feedback_patient/<appointment_id>', methods=['GET', 'POST'])
@login_required
def give_feedback_patient(appointment_id): 
    existing_feedback_cursor = Feedback.get_by_appointment(appointment_id)
    existing_feedback = next(existing_feedback_cursor, None)
    print("aaaexisting_feedback", existing_feedback)
    if request.method == 'POST':
        print("request.form", request.form)
        feedback_text = request.form.get("feedback_text")
        print("aaafeedback_text", feedback_text)
        rating = request.form.get("rating")
        print("aaaarating", rating)

        feedback_data = {
            "appointment_id": appointment_id,
            "feedback_text": feedback_text,
            "rating": rating
        }

        # Check if updating existing feedback or creating new feedback
        if existing_feedback:
            print("aaaaaa", feedback_data)
            print("aaaaaa-ext-id", existing_feedback['_id'])
            Feedback.update(existing_feedback['_id'], feedback_data)
            flash("Feedback updated successfully!", "success")
        else:
            Feedback.create(feedback_data)
            flash("Feedback submitted successfully!", "success")

        return redirect(url_for('view_patient_appointments'))

    return render_template('feedback/give_feedback_patient.html', appointment_id=appointment_id, existing_feedback=existing_feedback)
