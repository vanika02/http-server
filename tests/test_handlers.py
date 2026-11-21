import json
import pytest 
import handlers

from concurrent.futures import ThreadPoolExecutor

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

def test_signup_invalid_utf8():
    status, _, body = handlers.signup(b"\xff\xfe\xfa")

    assert status == 400 
    assert json.loads(body)["message"] == "Invalid JSON"

def test_signup_missing_username():
    status, _, body = handlers.signup(
        '{"password": "1234"}'
    )

    assert status == 400
    assert json.loads(body)["message"] == "Missing or invalid username"

def test_signup_empty_username():
    status, _, body = handlers.signup(
        '{"username": "     ", "password": "1234"}'
    )

    assert status == 400
    assert json.loads(body)["message"] == "Missing or invalid username"

def test_signup_empty_password():
    status, _, body = handlers.signup(
        '{"username": "Rani", "password": ""}'
    )

    assert status == 400
    assert json.loads(body)["message"] == "Missing or invalid password"

def test_login_unknown_user():
    status, _, body = handlers.login(
        '{"username": "unknown", "password": "1234"}'
    )

    assert status == 401
    assert json.loads(body)["message"] == "Invalid credentials"

def test_concurrent_signup_same_username():
    body = '{"username": "Rani", "password": "1234"}'

    barrier = threading.Barrier(2)

    def register():
        barrier.wait()
        return handlers.signup(body)[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(register)
            for _ in range(2)
        ]

        statuses = [future.result() for future in futures]
    
    assert sorted(statuses) == [201, 409]
    assert list(handlers.users.keys()) == ["Rani"]