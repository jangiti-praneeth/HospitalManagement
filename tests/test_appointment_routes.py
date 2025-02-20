from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template
from app.models.doctor import Doctor
import pytest
from app import app



import pytest

class TestBookAppointment:

    # User is a patient and submits a valid doctor_id, date, time_slot, payment_method, and amount. The appointment is created with status "Pending", payment details are saved, and appointment status is changed to "Paid" if payment_method is a card, otherwise it remains "Pending". Flash messages are displayed for each successful operation, and the user is redirected to view their appointments.
    def test_valid_appointment_creation_with_payment(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session["user_type"] = "patient"
                session["user_id"] = "patient_id"

            response = client.post("/book_appointment", data={
                "doctor_id": "doctor_id",
                "date": "2022-01-01",
                "time_slot": "09:00",
                "payment_method": "credit_card",
                "amount": "100"
            })

            assert response.status_code == 302
            assert response.location == "http://127.0.0.1:5000/view_patient_appointments"
            assert b"Appointment booked successfully! Status is pending." in response.data
            assert b"Payment details saved successfully!" in response.data
            assert b"Appointment status changed successfully!" in response.data

    # User is a patient and submits a valid doctor_id, date, and time_slot, but payment_method and amount are not submitted. The appointment is created with status "Pending", and flash messages are displayed for each successful operation. The user is redirected to view their appointments.
    def test_valid_appointment_creation_without_payment(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session["user_type"] = "patient"
                session["user_id"] = "patient_id"

            response = client.post("/book_appointment", data={
                "doctor_id": "doctor_id",
                "date": "2022-01-01",
                "time_slot": "09:00"
            })

            assert response.status_code == 302
            assert response.location == "http://localhost/view_patient_appointments"
            assert b"Appointment booked successfully! Status is pending." in response.data

    # User is a patient and submits a valid doctor_id, date, and time_slot, but the selected time slot has already been booked by someone else. An error flash message is displayed, and the user is redirected back to the book appointment page with the available slots updated.
    def test_already_booked_time_slot(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session["user_type"] = "patient"
                session["user_id"] = "patient_id"

            response = client.post("/book_appointment", data={
                "doctor_id": "doctor_id",
                "date": "2022-01-01",
                "time_slot": "09:00"
            })

            assert response.status_code == 200
            assert b"The selected time slot has just been booked by someone else. Please choose a different slot." in response.data

    # User is not logged in. They are redirected to the login page.
    def test_unauthorized_access(self):
        with app.test_client() as client:
            response = client.post("/book_appointment")

            assert response.status_code == 302
            assert response.location == "http://localhost/login"
            assert b"Unauthorized access." in response.data