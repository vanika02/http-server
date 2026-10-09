import pytest

from server import _read_one_request
from exceptions import HTTPParseError

class FakeSocket:

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def recv(self, size):
        return next(self.chunks)

def test_reads_complete_request():

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 14\r\n"
        b"\r\n"
        b'{"name":"bob"}'
    )

    sock = FakeSocket([request])
    buffer = bytearray()

    result = _read_one_request(
        sock,
        buffer
    )

    assert result is not None 

    raw_request, method, path, http_version, headers, body = result

    assert bytes(raw_request) == request
    assert method == "POST"
    assert path == "/signup"
    assert http_version == "HTTP/1.1"
    assert headers["content-length"] == "14"
    assert body == b'{"name":"bob"}'


def test_request_split_across_multiple_recv_calls():

    part1 = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 14\r\n"
        b"\r\n"
        b'{"name":'
    )

    part2 = b'"bob"}'

    expected = part1 + part2

    sock = FakeSocket([
        part1,
        part2,
    ])

    buffer = bytearray()

    result = _read_one_request(
        sock,
        buffer
    )

    assert result is not None 

    raw_request = result[0]

    assert bytes(raw_request) == expected

def test_two_requests_in_one_recv():

    request1 = (
        b"GET / HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
    )

    request2 = (
        b"GET /about HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )

    sock = FakeSocket([
        request1 + request2
    ])

    buffer = bytearray()

    result1 = _read_one_request(
        sock,
        buffer 
    )

    assert result1 == request1 

    assert result1 is not None
    assert bytes(request1[0]) == request1

    result2 = _read_one_request(
        sock,
        buffer 
    )

    assert result2 is not None 
    assert bytes(result2[0]) == request2

def test_request_body_and_next_request():

    request1 = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 14\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
        b'{"name":"bob"}'
    )

    request2 = (
        b"GET /about HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )

    sock = FakeSocket([
        request1 + request2
    ])

    buffer = bytearray()

    raw_request1 = _read_one_request(
        sock,
        buffer
    )

    assert raw_request1 == request1 
    assert buffer == bytearray(request2)

    raw_request2 = _read_one_request(
        sock,
        buffer 
    )

    assert raw_request2 == request2
    assert buffer == bytearray()

def test_incomplete_body_raises_error():

    request_headers = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 10\r\n"
        b"\r\n"
    )

    sock = FakeSocket([
        request_headers + b"Hello",
        b"",
    ])

    buffer = bytearray()

    with pytest.raises(ConnectionError):
        _read_one_request(
            sock,
            buffer
        )

def test_invalid_content_length_raises_error():

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: abc\r\n"
        b"\r\n"
    )

    sock = FakeSocket([request])
    buffer = bytearray()

    with pytest.raises(HTTPParseError):
        _read_one_request(
            sock,
            buffer
        )

def test_negative_content_length_raises_error():

    request = (
        b"POST /HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: -10\r\n"
        b"\r\n"
    )

    sock = FakeSocket([request])
    buffer = bytearray()

    with pytest.raises(HTTPParseError):
        _read_one_request(
            sock,
            buffer
        )

def test_empty_content_length_raises_error():

    request = (
        b"POST /HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length:\r\n"
        b"\r\n"
    )

    sock = FakeSocket([request])
    buffer = bytearray()

    with pytest.raises(HTTPParseError):
        _read_one_request(
            sock,
            buffer
        )