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

def test_valid_extension_method():
    request = (
        b"PATCH /resource HTTP/1.1\r\n"
        b"Host: localhost"
    )

    method, path, version, headers, content_length = (
        parse_request_head(request)
    )

    assert method == "PATCH"
    assert path == "/resource"
    assert version == "HTTP/1.1"

def test_invalid_header_name_with_whitespace_before_colon():
    request = (
        b"GET / HTTP/1.1\r\n"
        b"Host : localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_invalid_header_name_with_space():
    request = (
        b"GET / HTTP/1.1\r\n"
        b"Content Length: 5"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_header_name_cannot_start_with_whitespace():
    request = (
        b"GET / HTTP/1.1\r\n"
        b" Host: localhost"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_folded_header_is_rejected():
    request = (
        b"GET / HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b" continuation"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

@pytest.mark.parametrize(
    "content_length",
    [b"+5", b"-5", b"5.0", b"abc", b""],
)
def test_invalid_content_length(content_length):
    request = (
        b"POST / HTTP/1.1\r\n"
        b"Content-Length: " + content_length
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_transfer_encoding_is_rejected():
    request = (
        b"POST / HTTP/1.1\r\n"
        b"Transfer-Encoding: chunked"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_transfer_encoding_with_content_length_is_rejected():
    request = (
        b"POST / HTTP/1.1\r\n"
        b"Content-Length: 5\r\n"
        b"Transfer-Encoding: chunked"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_valid_content_length():
    request = (
        b"POST / HTTP/1.1\r\n"
        b"Content-Length: 25"
    )

    _, _, _, headers, content_length = parse_request_head(request)

    assert headers["content-length"] == "25"
    assert content_length == 25

def test_missing_host_header():
    request = b"GET / HTTP/1.1"

    with pytest.raises(HTTPParseError):
        parse_request_head(request)