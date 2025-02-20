from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template
from app.models.patient import Patient
from app.models.prescription import Prescription
from bson.objectid import ObjectId
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_view_patient_on_appointment_with_existing_patient_and_prescription(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = str(ObjectId())
    patient_data = {"_id": "1", "name": "John Doe"}
    prescription_data = {"_id": "1", "appointment": appointment_id, "prescription_text": "Test prescription", "medication": "Test medication"}
    mocker.patch.object(Patient, 'get_by_appointment', return_value=patient_data)
    mocker.patch.object(Prescription, 'get_by_appointment', return_value=prescription_data)

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment2/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>View Patient on Appointment</title>' in response.data
    assert b'<h1>View Patient on Appointment</h1>' in response.data
    assert b'John Doe' in response.data
    assert b'Test prescription' in response.data
    assert b'Test medication' in response.data


def test_view_patient_on_appointment_with_nonexistent_patient(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = str(ObjectId())
    mocker.patch.object(Patient, 'get_by_appointment', return_value=None)

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment2/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'No patient found for this appointment.' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_view_patient_on_appointment_with_existing_prescription(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = str(ObjectId())
    patient_data = {"_id": "1", "name": "John Doe"}
    prescription_data = {"_id": "1", "appointment": appointment_id, "prescription_text": "Test prescription", "medication": "Test medication"}
    mocker.patch.object(Patient, 'get_by_appointment', return_value=patient_data)
    mocker.patch.object(Prescription, 'get_by_appointment', return_value=prescription_data)

    # Make a POST request to the view_patient_on_appointment route
    response = client.post(f'/view_patient_on_appointment2/{appointment_id}', data={"prescription_text": "Updated prescription", "medication": "Updated medication"})

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Prescription updated successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_view_patient_on_appointment_with_nonexistent_prescription(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = str(ObjectId())
    patient_data = {"_id": "1", "name": "John Doe"}
    mocker.patch.object(Patient, 'get_by_appointment', return_value=patient_data)
    mocker.patch.object(Prescription, 'get_by_appointment', return_value=None)

    # Make a POST request to the view_patient_on_appointment route
    response = client.post(f'/view_patient_on_appointment2/{appointment_id}', data={"prescription_text": "New prescription", "medication": "New medication"})

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Prescription created successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data