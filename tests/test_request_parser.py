import pytest

from exceptions import HTTPParseError
from request_parser import parse_request_head


def test_malformed_header_raises_error():

    request = (
        b"GET / HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"BrokenHeader"
    )
    
    with pytest.raises(HTTPParseError):
        parse_request_head(request)



def test_duplicate_content_length_raises_error():

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 5\r\n"
        b"Content-Length: 5"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)