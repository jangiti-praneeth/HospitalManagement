from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template, request, flash
from app.models.Schedule import Schedule
from bson.objectid import ObjectId
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_update_schedule_with_post_request(client: FlaskClient, mocker):
    # Mock the necessary data
    session["user_type"] = "doctor"
    session["user_id"] = "1"
    mocker.patch.object(request, 'method', return_value='POST')
    mocker.patch.object(request.form, 'getlist', return_value=["Monday", "Wednesday"])
    mocker.patch.object(request.form, 'get', side_effect=["09:00", "17:00"])
    mocker.patch.object(Schedule, 'get_by_doctor_id', return_value={"_id": ObjectId("1"), "days": ["Tuesday", "Thursday"], "start_time": "08:00", "end_time": "16:00"})
    mocker.patch.object(Schedule, 'update')

    # Make a POST request to the update_schedule route
    response = client.post('/update_schedule')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Schedule updated successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_update_schedule_with_get_request(client: FlaskClient, mocker):
    # Mock the necessary data
    session["user_type"] = "doctor"
    session["user_id"] = "1"
    mocker.patch.object(request, 'method', return_value='GET')
    mocker.patch.object(Schedule, 'get_by_doctor_id', return_value={"_id": ObjectId("1"), "days": ["Monday", "Wednesday"], "start_time": "09:00", "end_time": "17:00"})

    # Make a GET request to the update_schedule route
    response = client.get('/update_schedule')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Update Schedule</title>' in response.data
    assert b'<h1>Update Schedule</h1>' in response.data