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
    assert join.loads(body)["message"] == "User created"
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