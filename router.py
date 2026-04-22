from handlers import home, about, api, not_found

def route(path):
    if path == "/":
        return home()
    
    elif path =="/about":
        return about()

    elif path == "/api":
        return api()
    
    else:
        return not_found()