from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template, request, flash
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.medication import Medication
from bson.objectid import ObjectId
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_view_patient_on_appointment_with_existing_patient(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(Patient, 'get_by_appointment', return_value={"_id": ObjectId(appointment_id)})
    mocker.patch.object(Prescription, 'get_by_appointment', return_value={"_id": ObjectId("prescription_id")})
    mocker.patch.object(Medication, 'get_by_prescription', return_value=[{"_id": ObjectId("medication_id")}])

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>View Patient on Appointment</title>' in response.data
    assert b'<h1>View Patient on Appointment</h1>' in response.data


def test_view_patient_on_appointment_with_nonexistent_patient(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(Patient, 'get_by_appointment', return_value=None)

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'No patient found for this appointment.' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_view_patient_on_appointment_with_existing_prescription(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(Patient, 'get_by_appointment', return_value={"_id": ObjectId(appointment_id)})
    mocker.patch.object(Prescription, 'get_by_appointment', return_value={"_id": ObjectId("prescription_id")})
    mocker.patch.object(Medication, 'get_by_prescription', return_value=None)

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>View Patient on Appointment</title>' in response.data
    assert b'<h1>View Patient on Appointment</h1>' in response.data


def test_view_patient_on_appointment_with_nonexistent_prescription(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(Patient, 'get_by_appointment', return_value={"_id": ObjectId(appointment_id)})
    mocker.patch.object(Prescription, 'get_by_appointment', return_value=None)

    # Make a GET request to the view_patient_on_appointment route
    response = client.get(f'/view_patient_on_appointment/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>View Patient on Appointment</title>' in response.data
    assert b'<h1>View Patient on Appointment</h1>' in response.data


def test_view_patient_on_appointment_with_post_request(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(Patient, 'get_by_appointment', return_value={"_id": ObjectId(appointment_id)})
    mocker.patch.object(Prescription, 'get_by_appointment', return_value={"_id": ObjectId("prescription_id")})
    mocker.patch.object(Medication, 'get_by_prescription', return_value=[{"_id": ObjectId("medication_id")}])
    mocker.patch.object(Prescription, 'update')
    mocker.patch.object(Prescription, 'create')

    # Make a POST request to the view_patient_on_appointment route
    response = client.post(f'/view_patient_on_appointment/{appointment_id}', data={
        "prescription_text": "Test Prescription",
        "medication": "Test Medication"
    })

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Prescription updated successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data