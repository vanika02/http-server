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
        body=""
    )

    result = response.build()

    header_bytes, body_bytes = result.split(b"\r\n\r\n", 1)

    assert header_bytes.startswith(b"HTTP/1.1 204 No Content")
    assert body_bytes == b""