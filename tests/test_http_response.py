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