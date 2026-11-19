from router import route 

def test_unknown_path_returns_404():
    status, content_type, body, headers = route("GET", "/unknown")

    assert status == 404
    assert body == "404 Not Found"
    assert headers == {}

def test_known_path_with_unsupported_method_returns_405():
    status, content_type, body, headers = route("POST", "/about")

    assert status == 405
    assert body == "405 Method Not Allowed"
    assert headers["Allow"] == "GET"

def test_supported_method_calls_handler():
    status, content_type, body, headers = route("GET", "/about")

    assert status == 200
    assert content_type == "text/plain"
    assert body == "This is the about page"
    assert headers == {}

def test_405_allow_header_for_signup():
    status, content_type, body, headers = route(
        "GET", "/signup"
    )

    assert status == 405
    assert headers["Allow"] == "POST"