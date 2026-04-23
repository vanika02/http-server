import json

users = {}

def home():
    return "200 OK", "text/plain", "Hello Dharampal"

def about():
    return "200 OK", "text/plain", "About Your Mom"

def api():
    data = {
        "name" : "Dharampal the great",
        "role" : "Tuzya ichi"
    }
    return "200 OK", "application/json", json.dumps(data)

def login(body):
    data = json.loads(body)

    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        return "200 OK", "application/json", json.dumps({
            "message": "Login success"
        }) 

    else:
        return "401 Unauthorized", "application/json", json.dumps({
            "message": "Invalid credentials"
        })
    
def signup(body):
    data = json.loads(body)

    username = data.get("username")
    password = data.get("password")

    if not username or password:
        return "400 Bad Request", "application/json", json.dumps({
            "message": "Missing username or password"
        })

    if username in users:
        return "409 confilct", "application/json", json.dumps({
            "message": "User already exists"
        })
    
    users[username] = password

    return "201 created", "application/json", json.dumps({
        "message": "User created"
    })

def not_found():
    return "404 You can't see me", "text/plain", "404 Not Found"