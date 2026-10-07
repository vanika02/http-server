import pytest

from exceptions import HTTPParseError
from request_parser import HTTPRequest


def test_malformed_header_raises_error():

    request = (
        b"GET / HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"BrokenHeader\r\n"
        b"\r\n"
    )
    
    with pytest.raises(HTTPParseError):
        HTTPRequest(request)



def test_duplicate_content_length_raises_error():

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 5\r\n"
        b"Content-Length: 5\r\n"
        b"\r\n"
        b"hell"
    )

    with pytest.raises(HTTPParseError):
        HTTPRequest(request)