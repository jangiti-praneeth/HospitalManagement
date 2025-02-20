from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template, request, flash
from app.models.doctor import Doctor
from app.models.patient import Patient
from bson.objectid import ObjectId
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_update_profile_with_post_request_doctor(client: FlaskClient, mocker):
    # Mock the necessary data
    session['user_id'] = "1"
    session['user_type'] = "doctor"
    mocker.patch.object(request, 'method', return_value='POST')
    mocker.patch.object(request.form, 'get', side_effect=["John Doe", "john@example.com", "1234567890", "123 Main St"])
    mocker.patch.object(Doctor.collection, 'update_one')

    # Make a POST request to the update_profile route
    response = client.post('/update_profile')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Profile updated successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_update_profile_with_post_request_patient(client: FlaskClient, mocker):
    # Mock the necessary data
    session['user_id'] = "2"
    session['user_type'] = "patient"
    mocker.patch.object(request, 'method', return_value='POST')
    mocker.patch.object(request.form, 'get', side_effect=["Jane Smith", "jane@example.com", "9876543210", "456 Elm St"])
    mocker.patch.object(Patient.collection, 'update_one')

    # Make a POST request to the update_profile route
    response = client.post('/update_profile')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Profile updated successfully!' in response.data
    assert b'<h1>Welcome to the Patient Dashboard</h1>' in response.data


def test_update_profile_with_post_request_invalid_user_type(client: FlaskClient):
    # Mock the necessary data
    session['user_id'] = "3"
    session['user_type'] = "invalid"
    mocker.patch.object(request, 'method', return_value='POST')

    # Make a POST request to the update_profile route
    response = client.post('/update_profile')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Invalid user type' in response.data
    assert b'<h1>Welcome to the Dashboard</h1>' in response.data


def test_update_profile_with_get_request_doctor(client: FlaskClient, mocker):
    # Mock the necessary data
    session['user_id'] = "1"
    session['user_type'] = "doctor"
    mocker.patch.object(Doctor.collection, 'find_one', return_value={"_id": ObjectId("1"), "name": "John Doe", "contactInfo": {"email": "john@example.com", "phone": "1234567890", "address": "123 Main St"}})

    # Make a GET request to the update_profile route
    response = client.get('/update_profile')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Update Profile</title>' in response.data
    assert b'<h1>Update Profile</h1>' in response.data
    assert b'value="John Doe"' in response.data
    assert b'value="john@example.com"' in response.data
    assert b'value="1234567890"' in response.data
    assert b'value="123 Main St"' in response.data


def test_update_profile_with_get_request_patient(client: FlaskClient, mocker):
    # Mock the necessary data
    session['user_id'] = "2"
    session['user_type'] = "patient"
    mocker.patch.object(Patient.collection, 'find_one', return_value={"_id": ObjectId("2"), "name": "Jane Smith", "contactInfo": {"email": "jane@example.com", "phone": "9876543210", "address": "456 Elm St"}})

    # Make a GET request to the update_profile route
    response = client.get('/update_profile')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Update Profile</title>' in response.data
    assert b'<h1>Update Profile</h1>' in response.data
    assert b'value="Jane Smith"' in response.data
    assert b'value="jane@example.com"' in response.data
    assert b'value="9876543210"' in response.data
    assert b'value="456 Elm St"' in response.data


def test_update_profile_with_get_request_invalid_user_type(client: FlaskClient):
    # Mock the necessary data
    session['user_id'] = "3"
    session['user_type'] = "invalid"

    # Make a GET request to the update_profile route
    response = client.get('/update_profile')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Invalid user type' in response.data
    assert b'<h1>Welcome to the Dashboard</h1>' in response.data