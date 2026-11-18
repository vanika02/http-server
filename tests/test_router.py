from router import route 

def test_unknown_path_returns_404():
    status, content_type, body = route("GET", "/unknown")

    assert status == 404
    assert body == "404 Not Found"

def test_known_path_with_unsupported_method_returns_405():
    status, content_type, body = route("POST", "/about")

    assert status == 405
    assert body == "405 Method Not Allowed"

def test_supported_method_calls_handler():
    status, content_type, body = route("GET", "/about")

    assert status == 200
    assert content_type == "text/plain"
    assert body == "About Your Mom"