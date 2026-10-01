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
        return "200", "application/json", json.dumps({
            "message": "Login success"
        }) 

    else:
        return "401", "application/json", json.dumps({
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