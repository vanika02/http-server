from handlers import home, about, api, not_found, login

def route(method, path, body=""):
    if method == "GET" and path == "/":
        return home()
    
    elif method == "GET" and  path =="/about":
        return about()

    elif method == "GET" and  path == "/api":
        return api()
    
    elif method == "POST" and path == "/login":
        return login(body)
    
    else:
        return not_found()