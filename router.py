from urllib.parse import urlsplit

from static_files import load_static_file
from handlers import home, about, api, not_found, login, signup


STATIC_URL_PREFIX = "/static/"

ROUTES = {
    "/": {"GET": home},
    "/about": {"GET": about},
    "/api": {"GET": api},
    "/login": {"POST": login},
    "/signup": {"POST": signup},
}


def route(method, path, body="", static_root=None):
    """Find and execute the handler for an HTTP request."""

    route_path = urlsplit(path).path

    if route_path.startswith(STATIC_URL_PREFIX):
        if method not in ("GET", "HEAD"):
            return (
                405,
                "text/plain",
                "405 Method Not Allowed",
                {"Allow": "GET, HEAD"},
            )

        if static_root is None:
            raise ValueError("static_root must be provided")

        try:
            response_body, content_type = load_static_file(
                path,
                static_root,
            )
        except (FileNotFoundError, IsADirectoryError):
            return (*not_found(), {})
        except PermissionError:
            return (403, "text/plain", "403 Forbidden", {})
        except ValueError:
            return (400, "text/plain", "400 Bad Request", {})

        return 200, content_type, response_body, {}

    if route_path not in ROUTES:
        return (*not_found(), {})

    allowed_methods = ROUTES[route_path]

    if method == "HEAD" and "GET" in allowed_methods:
        handler = allowed_methods["GET"]
    elif method in allowed_methods:
        handler = allowed_methods[method]
    else:
        allowed = list(allowed_methods.keys())

        if "GET" in allowed_methods:
            allowed.append("HEAD")

        return (
            405,
            "text/plain",
            "405 Method Not Allowed",
            {"Allow": ", ".join(allowed)}
        )

    if method == "POST":
        status, content_type, response_body = handler(body)
    else:
        status, content_type, response_body = handler()

    return status, content_type, response_body, {}
