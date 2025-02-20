from flask.testing import FlaskClient
from flask import session, url_for, redirect, render_template, request, flash
from app.models.payment import Payment
from datetime import datetime
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_make_payment_with_post_request(client: FlaskClient, mocker):
    # Mock the necessary data
    appointment_id = "1"
    mocker.patch.object(request, 'method', return_value='POST')
    mocker.patch.object(request.form, 'get', side_effect=["100", "cash"])
    mocker.patch.object(Payment, 'create')

    # Make a POST request to the make_payment route
    response = client.post(f'/make_payment/{appointment_id}')

    # Assert the response status code
    assert response.status_code == 302

    # Assert the flash message and redirection
    assert b'Payment made successfully!' in response.data
    assert b'<h1>Welcome to the Doctor Dashboard</h1>' in response.data


def test_make_payment_with_get_request(client: FlaskClient):
    # Make a GET request to the make_payment route
    response = client.get('/make_payment/1')

    # Assert the response status code
    assert response.status_code == 200

    # Assert the rendered template
    assert b'<title>Make Payment</title>' in response.data
    assert b'<h1>Make Payment</h1>' in response.data