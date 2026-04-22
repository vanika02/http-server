import json

def home():
    return "200 OK", "text/plain", "Hello Dharampal"

def about():
    return "200 OK", "text/plain", "About Your Mom"

def api():
    data = {
        "name" : "Dharampal the great",
        "role" : "Tuzya ichi"
    }
    return "200 OK", "application/json", json.dump(data)

    
def not_found():
    return "404 You can't see me", "text/plain", "404 Not Found"