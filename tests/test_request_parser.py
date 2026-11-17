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

def test_unsupported_http_version():
    request = (
        b"GET / HTTP/2.0\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_empty_request_target():
    request = (
        b"GET HTTP/1.1\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_malformed_request_line():
    request = (
        b"GET / HTTP/1.1 EXTRA\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_invalid_method_token():
    request = (
        b"GE@T / HTTP/1.1\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_repeated_spaces_in_request_line():
    request = (
        b"GET      / HTTP/1.1\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_tab_seperator_in_request_line():
    request = (
        b"GET\t/\tHTTP/1.1\r\n"
        b"Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)