from app.models.payment import Payment
from app.models.prescription import Prescription
from flask import render_template, request, redirect, url_for, session
from app import app 
from .decorators import login_required
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@app.route('/make_payment/<appointment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(appointment_id):
    if request.method == 'POST':
        amount = request.form.get("amount")
        payment_mode = request.form.get("payment_mode")
        
        payment_data = {
            "appointment": appointment_id,
            "amount": amount,
            "payment_mode": payment_mode,
            "status": "completed",
            "date": datetime.now().date(),
            "time": datetime.now().time()
        }
        
        Payment.create(payment_data)
        flash("Payment made successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('make_payment.html')
