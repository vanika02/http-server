import json

users = {}

def json_response(status_code, message):
    """Create a consistent JSON response."""
    return (
        status_code,
        "application/json",
        json.dumps({"message": message})
    )

def parse_user_data(body):
    """
    Parse and validate the request body.

    Returns:
        dict: Validated user data.

    Raises:
        ValueError: If JSON is invalid or not a JSON object.
    """

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON") from exc 
    
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        raise ValueError("Missing or invalid username")

    if not isinstance(password, str) or not password:
        raise ValueError("Missing or invalid password")
    
    return {
        "username": username.strip(),
        "password": password
    }

def home():
    return 200, "text/plain", "Hello, Welcome to the http-server home page"

def about():
    return 200, "text/plain", "This is the about page"

def api():
    data = {
        "name" : "Vanika",
        "role" : "Creator"
    }

    return 200, "application/json", json.dumps(data)

def login(body):
    try:
        data = parse_user_data(body)
    except ValueError as exc:
        return json_response(400, str(exc))

    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        return json_response(200, "Login success")

    return json_response(401, "Invalid credentials")
    
def signup(body):
    try:
        data = parse_user_data(body)
    except ValueError as exc:
        return json_response(400, str(exc))

    username = data.get("username")
    password = data.get("password")

    if username in users:
        return json_response(409, "User already exists")

    users[username] = password

    # print("USERS AFTER:", users)

    return json_response(201, "User created")

    
def not_found():
    return 404, "text/plain", "404 Not Found"