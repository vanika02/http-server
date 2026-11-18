from router import route 

def test_unknown_path_returns_404():
    status, content_type, body = route("GET", "/unknown")

    assert status == 404
    assert body == "404 Not Found"