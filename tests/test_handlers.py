import json
import pytest 

import handlers

@pytest.fixture(autouse=True)
def reset_users():
    handlers.users.clear()

def test_signup_success():
    status, content_type, body = handlers.signup(
        '{"username": "Rani", "password": "1234"}'
    )

    assert status == 201
    assert content_type == "application/json"
    assert json.loads(body)["message"] == "User created"
    assert handlers.users["Rani"] == "1234"

def test_signup_duplicate_user():
    handlers.users["Rani"] = "1234"

    status, _, body = handlers.signup(
        '{"username": "Rani", "password": "another"}'
    )

    assert status == 409
    assert json.loads(body)["message"] == "User already exists"

def test_signup_invalid_json():
    status, _, body = handlers.signup("{invalid}")

    assert status == 400
    assert json.loads(body)["message"] == "Invalid JSON"

@pytest.mark.parametrize("body", [
    "[]",
    '"hello"',
    "null",
    "123"
])
def test_signup_non_object_json(body):
    status, _, response_body = handlers.signup(body)

    assert status == 400
    assert json.loads(response_body)["message"] == "JSON body must be an object"


def test_signup_missing_fields():
    status, _, body = handlers.signup(
        '{"username": "alice"}'
    )

    assert status == 400
    assert json.loads(body)["message"] == "Missing or invalid password"

def test_login_success():
    handlers.users["Rani"] = "1234"

    status, _, body = handlers.login(
        '{"username": "Rani", "password": "1234"}'
    )

    assert status == 200
    assert json.loads(body)["message"] == "Login success"

def test_login_invalid_credentials():
    handlers.users["Rani"] = "1234"

    status, _, body = handlers.login(
        '{"username": "Rani", "password": "wrong"}'
    )

    assert status == 401 
    assert json.loads(body)["message"] == "Invalid credentials"

def test_login_invalid_json():
    status, _, body = handlers.login("{invalid}")

    assert status == 400
    assert json.loads(body)["message"] == "Invalid JSON"