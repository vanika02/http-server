from urllib.parse import urlsplit

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
    """Find and execute the handler for an HTTP request."""

    route_path = urlsplit(path).path 

    if route_path not in ROUTES:
        return (*not_found(), {})

    allowed_methods = ROUTES[route_path]

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