from handlers import home, about, api, not_found, login, signup

ROUTES = {
    "/": {
        "GET": home,
    },
    "/about": {
        "GET": about,
    },
    "/api": {
        "GET": api,
    },
    "/login": {
        "POST": login,
    },
    "/signup": {
        "POST": signup
    },
}

def route(method, path, body=""):
    
    if path not in ROUTES:
        return not_found()

    allowed_methods = ROUTES[path]

    if method not in allowed_methods:
        return (
            405,
            "text/plain",
            "405 Method Not Allowed",
        )

    handler = allowed_methods[method]

    if method == "POST":
        return handler(body)
    
    return handler()