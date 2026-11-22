import pytest

from request_parser import (
    parse_request_head,
    read_chunked_body,
    IncompleteChunkError,
)
from exceptions import HTTPParseError

def test_parse_chunked_header():
    request = (
        b"POST /submit HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"\r\n"
    )

    *_, content_length, is_chunked = parse_request_head(request)

    assert content_length == 0
    assert is_chunked is True


def test_parse_content_length_header():
    request = (
        b"POST /submit HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 5\r\n"
        b"\r\n"
    )

    *_, content_length, is_chunked = parse_request_head(request)

    assert content_length == 5
    assert is_chunked is False


def test_reject_content_length_with_transfer_encoding():
    request = (
        b"POST /submit HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 5\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"\r\n"
    )

    with pytest.raises(HTTPParseError):
        parse_request_head(request)

def test_decode_single_chunk():
    data = b"5\r\nHello\r\n0\r\n\r\n"

    body, consumed = read_chunked_body(data)

    assert body == b"Hello"
    assert consumed == len(data)


def test_decode_multiple_chunks():
    data = b"4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n"

    body, consumed = read_chunked_body(data)

    assert body == b"Wikipedia"
    assert consumed == len(data)


def test_decode_empty_body():
    data = b"0\r\n\r\n"

    body, consumed = read_chunked_body(data)

    assert body == b""
    assert consumed == len(data)


def test_decode_hex_chunk_size():
    data = b"a\r\n0123456789\r\n0\r\n\r\n"

    body, consumed = read_chunked_body(data)

    assert body == b"0123456789"
    assert consumed == len(data)


def test_decode_uppercase_hex_chunk_size():
    data = b"A\r\n0123456789\r\n0\r\n\r\n"

    body, _ = read_chunked_body(data)

    assert body == b"0123456789"


def test_decode_chunk_with_extension():
    data = b"5;name=value\r\nHello\r\n0\r\n\r\n"

    body, consumed = read_chunked_body(data)

    assert body == b"Hello"
    assert consumed == len(data)


def test_decode_chunk_with_trailer():
    data = (
        b"5\r\nHello\r\n"
        b"0\r\n"
        b"X-Checksum: abc123\r\n"
        b"\r\n"
    )

    body, consumed = read_chunked_body(data)

    assert body == b"Hello"
    assert consumed == len(data)


def test_preserve_bytes_after_chunked_body():
    data = b"5\r\nHello\r\n0\r\n\r\nNEXT"

    body, consumed = read_chunked_body(data)

    assert body == b"Hello"
    assert data[consumed:] == b"NEXT"

def test_reject_invalid_chunk_size():
    data = b"xyz\r\nHello\r\n0\r\n\r\n"

    with pytest.raises(HTTPParseError):
        read_chunked_body(data)


def test_reject_missing_chunk_crlf():
    data = b"5\r\nHelloXX0\r\n\r\n"

    with pytest.raises(HTTPParseError):
        read_chunked_body(data)


def test_reject_body_size_limit():
    data = b"5\r\nHello\r\n0\r\n\r\n"

    with pytest.raises(HTTPParseError):
        read_chunked_body(data, max_body_size=4)


def test_body_size_exactly_at_limit_is_accepted():
    data = b"5\r\nHello\r\n0\r\n\r\n"

    body, _ = read_chunked_body(data, max_body_size=5)

    assert body == b"Hello"

def test_incomplete_chunk_data():
    data = b"5\r\nHel"

    with pytest.raises(IncompleteChunkError):
        read_chunked_body(data)


def test_incomplete_chunk_terminator():
    data = b"5\r\nHello"

    with pytest.raises(IncompleteChunkError):
        read_chunked_body(data)


def test_incomplete_missing_final_chunk():
    data = b"5\r\nHello\r\n"

    with pytest.raises(IncompleteChunkError):
        read_chunked_body(data)


def test_incomplete_chunk_size_line():
    data = b"5"

    with pytest.raises(IncompleteChunkError):
        read_chunked_body(data)