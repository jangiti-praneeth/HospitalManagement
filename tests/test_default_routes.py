from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template
from app.models.doctor import Doctor
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route_redirects_to_doctor_dashboard_when_user_type_is_doctor(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value="doctor")
    mocker.patch.object(Doctor, 'get_all_doctors', return_value=[{"_id": "1", "name": "Dr. John Doe"}])

    # Make a GET request to the index route
    response = client.get('/')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the redirect to the doctor_dashboard route
    assert response.headers['Location'] == url_for('doctor_dashboard', _external=True)


def test_index_route_redirects_to_patient_dashboard_when_user_type_is_patient(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value="patient")
    mocker.patch.object(Doctor, 'get_all_doctors', return_value=[{"_id": "1", "name": "Dr. John Doe"}])

    # Make a GET request to the index route
    response = client.get('/')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the redirect to the patient_dashboard route
    assert response.headers['Location'] == url_for('patient_dashboard', _external=True)


def test_index_route_renders_index_template_with_doctors_when_user_not_logged_in(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value=None)
    mocker.patch.object(Doctor, 'get_all_doctors', return_value=[{"_id": "1", "name": "Dr. John Doe"}])

    # Make a GET request to the index route
    response = client.get('/')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Hospital Management System</title>' in response.data
    assert b'<h1>Welcome to the Hospital Management System</h1>' in response.data
    assert b'<h2>Available Doctors:</h2>' in response.data
    assert b'Dr. John Doe' in response.data