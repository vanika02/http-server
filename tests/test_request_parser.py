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