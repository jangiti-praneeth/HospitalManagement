from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template
from app.models.feedback import Feedback
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_give_feedback_patient_route_get_method(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value="patient")
    appointment_id = "1"

    # Make a GET request to the give_feedback_patient route
    response = client.get(f'/give_feedback_patient/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Give Feedback</title>' in response.data
    assert b'<h1>Give Feedback</h1>' in response.data
    assert b'<form action="/give_feedback_patient/1" method="POST">' in response.data


def test_give_feedback_patient_route_post_method_with_existing_feedback(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value="patient")
    appointment_id = "1"
    feedback_text = "Great service!"
    rating = "5"

    # Mock the Feedback.get_by_appointment method
    mocker.patch.object(Feedback, 'get_by_appointment', return_value=[{"_id": "1", "appointment_id": "1", "feedback_text": "Good job!", "rating": "4"}])

    # Make a POST request to the give_feedback_patient route
    response = client.post(f'/give_feedback_patient/{appointment_id}', data={"feedback_text": feedback_text, "rating": rating})

    # Assert the response status code
    assert response.status_code == 302

    # Assert the redirect to the view_patient_appointments route
    assert response.headers['Location'] == url_for('view_patient_appointments', _external=True)

    # Assert that Feedback.update method is called
    Feedback.update.assert_called_once_with("1", {"appointment_id": "1", "feedback_text": feedback_text, "rating": rating})

    # Assert that the flash message is set
    with client.session_transaction() as session:
        assert session['_flashes'] == [('success', 'Feedback updated successfully!')]


def test_give_feedback_patient_route_post_method_without_existing_feedback(client: FlaskClient, mocker):
    # Mock the necessary session data
    mocker.patch.object(session, 'get', return_value="patient")
    appointment_id = "1"
    feedback_text = "Great service!"
    rating = "5"

    # Mock the Feedback.get_by_appointment method
    mocker.patch.object(Feedback, 'get_by_appointment', return_value=None)

    # Make a POST request to the give_feedback_patient route
    response = client.post(f'/give_feedback_patient/{appointment_id}', data={"feedback_text": feedback_text, "rating": rating})

    # Assert the response status code
    assert response.status_code == 302

    # Assert the redirect to the view_patient_appointments route
    assert response.headers['Location'] == url_for('view_patient_appointments', _external=True)

    # Assert that Feedback.create method is called
    Feedback.create.assert_called_once_with({"appointment_id": "1", "feedback_text": feedback_text, "rating": rating})

    # Assert that the flash message is set
    with client.session_transaction() as session:
        assert session['_flashes'] == [('success', 'Feedback submitted successfully!')]