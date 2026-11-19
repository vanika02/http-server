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
    return 200, "text/plain", "Hello Dharampal"

def about():
    return 200, "text/plain", "About Your Mom"

def api():
    data = {
        "name" : "Dharampal the great",
        "role" : "Tuzya ichi"
    }
    return 200, "application/json", json.dumps(data)

def login(body):
    data = json.loads(body)

    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        return 200, "application/json", json.dumps({
            "message": "Login success"
        }) 

    else:
        return 401, "application/json", json.dumps({
            "message": "Invalid credentials"
        })
    
def signup(body):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return 400, "application/json", json.dumps({
            "message": "Invalid JSON"
        })

    username = data.get("username")
    password = data.get("password")


    if not username or not password:
        return 400, "application/json", json.dumps({
            "message": "Missing username or password"
        })
    
    if username in users:
        # print("USER ALREADY EXISTS")
        return 409, "application/json", json.dumps({
            "message": "User already exists"
        })
    

    users[username] = password

    print("USERS AFTER:", users)

    return 201, "application/json", json.dumps({
        "message": "User created"
    })

    
def not_found():
    return 404, "text/plain", "404 Not Found"