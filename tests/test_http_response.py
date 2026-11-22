import pytest 

from http_response import HTTPResponse

def test_correct_status_line():
    response = HTTPResponse(
        status_code=201,
        body="User created"
    )

    result = response.build()

    assert result.startswith(b"HTTP/1.1 201 Created\r\n")

def test_content_length_for_utf8_body():
    body = "नमस्ते"

    response = HTTPResponse(body=body)

    result = response.build()

    expected_length = len(body.encode("utf-8"))

    assert f"Content-Length: {expected_length}".encode() in result

def test_caller_provided_content_type_is_preserved():
    response = HTTPResponse(
        headers={"Content-Type": "application/json"},
        body='{"message": "success"}'
    )

    result = response.build()

    assert b"Content-Type: application/json" in result
    assert b"Content-Type: text/plain; charset=utf-8" not in result

def test_default_connection_header_is_present():
    response = HTTPResponse()

    result = response.build()

    assert b"Connection: close" in result

def test_204_no_content_has_no_body():
    response = HTTPResponse(
        status_code=204,
        body="This must not be sent"
    )

    result = response.build()

    header_bytes, body_bytes = result.split(b"\r\n\r\n", 1)

    assert header_bytes.startswith(b"HTTP/1.1 204 No Content")
    assert body_bytes == b""


def test_response_supports_binary_body():
    body = bytes([0, 255, 128, 10, 65])

    response = HTTPResponse(
        status_code=200,
        headers={"Content-Type": "application/octet-stream"},
        body=body,
    )

    result = response.build()
    headers, response_body = result.split(b"\r\n\r\n", 1)

    assert b"Content-Length: 5" in headers
    assert response_body == body


def test_response_rejects_unsupported_body_type():
    response = HTTPResponse(
        status_code=200,
        body={"message": "hello"},
    )

    with pytest.raises(TypeError):
        response.build()
