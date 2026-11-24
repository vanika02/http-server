from router import route


def test_health_returns_200():
    status, content_type, body, headers = route(
        "GET",
        "/health",
    )

    assert status == 200
    assert content_type == "application/json"
    assert body == '{"status": "ok"}'
    assert headers == {}


def test_health_returns_valid_json():
    import json

    status, content_type, body, headers = route(
        "GET",
        "/health",
    )

    data = json.loads(body)

    assert data == {"status": "ok"}


def test_head_health_uses_get_handler():
    status, content_type, body, headers = route(
        "HEAD",
        "/health",
    )

    assert status == 200
    assert content_type == "application/json"
    assert body == '{"status": "ok"}'


def test_health_rejects_unsupported_method():
    status, content_type, body, headers = route(
        "POST",
        "/health",
    )

    assert status == 405
    assert headers["Allow"] == "GET, HEAD"