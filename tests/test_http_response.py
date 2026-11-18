import pytest 

from http_response import HTTPResponse

def test_correct_status_line():
    response = HTTPResponse(
        status_code=201,
        body="User created"
    )

    result = response.build()

    assert result.startswith(b"HTTP/1.1 201 Created\r\n")