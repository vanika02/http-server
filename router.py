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
        status, content_type, response_body = not_found()
        return status, content_type, response_body, {}

    allowed_methods = ROUTES[path]

    if method not in allowed_methods:
        return (
            405,
            "text/plain",
            "405 Method Not Allowed",
            {
                "Allow": ", ".join(allowed_methods.keys())
            }
        )

    handler = allowed_methods[method]

    if method == "POST":
        status, content_type, response_body = handler(body)
    else:
        status, content_type, response_body = handler()
    
    return status, content_type, response_body, {}