
import socket
import threading
import time

import pytest

from config import ServerConfig
from server import handle_client


def run_server_request(request, config=None, fragments=None):
    """
    Send an HTTP request through a real socket pair and return
    the complete server response.
    """
    if config is None:
        config = ServerConfig(socket_timeout=2)

    server_socket, client_socket = socket.socketpair()

    server_thread = threading.Thread(
        target=handle_client,
        args=(server_socket, config),
        daemon=True,
    )
    server_thread.start()

    try:
        if fragments:
            for fragment in fragments:
                client_socket.sendall(fragment)
                time.sleep(0.01)
        else:
            client_socket.sendall(request)

        # Tell the server that no more request bytes are coming.
        client_socket.shutdown(socket.SHUT_WR)

        response = bytearray()

        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response.extend(data)

        return bytes(response)

    finally:
        client_socket.close()
        server_thread.join(timeout=3)

        assert not server_thread.is_alive(), (
            "Server thread did not terminate"
        )


def make_chunked_request(body_chunks, extra_headers=b""):
    """
    Build a chunked POST request from a list of byte chunks.
    """
    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        + extra_headers
        + b"\r\n"
    )

    for chunk in body_chunks:
        request += (
            f"{len(chunk):X}\r\n".encode()
            + chunk
            + b"\r\n"
        )

    request += b"0\r\n\r\n"

    return request


def test_single_chunk_request():
    body = b'{"username":"chunkuser1","password":"secret"}'

    request = make_chunked_request([body])

    response = run_server_request(request)

    assert b"201 Created" in response
    assert b"User created" in response


def test_multiple_chunks_are_combined():
    body_chunks = [
        b'{"username":',
        b'"chunkuser2",',
        b'"password":',
        b'"secret"}',
    ]

    request = make_chunked_request(body_chunks)

    response = run_server_request(request)

    assert b"201 Created" in response
    assert b"User created" in response


def test_chunked_request_with_chunk_extensions():
    body = b'{"username":"chunkuser3","password":"secret"}'

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        + f"{len(body):X};name=test\r\n".encode()
        + body
        + b"\r\n"
        + b"0\r\n\r\n"
    )

    response = run_server_request(request)

    assert b"201 Created" in response
    assert b"User created" in response


def test_chunked_request_with_trailers():
    body = b'{"username":"chunkuser4","password":"secret"}'

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        + f"{len(body):X}\r\n".encode()
        + body
        + b"\r\n"
        + b"0\r\n"
        + b"X-Checksum: test-value\r\n"
        + b"\r\n"
    )

    response = run_server_request(request)

    assert b"201 Created" in response
    assert b"User created" in response


def test_chunked_request_split_across_tcp_reads():
    body = b'{"username":"chunkuser5","password":"secret"}'

    request = make_chunked_request([
        body[:10],
        body[10:25],
        body[25:],
    ])

    # Split the wire request into small pieces to exercise
    # partial reads of headers, chunk sizes, and chunk data.
    fragments = [
        request[i:i + 7]
        for i in range(0, len(request), 7)
    ]

    response = run_server_request(
        request,
        fragments=fragments,
    )

    assert b"201 Created" in response
    assert b"User created" in response


def test_chunked_request_followed_by_another_request():
    body = b'{"username":"chunkuser6","password":"secret"}'

    first_request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
        + f"{len(body):X}\r\n".encode()
        + body
        + b"\r\n"
        + b"0\r\n\r\n"
    )

    second_request = (
        b"GET /about HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )

    response = run_server_request(
        first_request + second_request
    )

    # Both requests must receive responses.
    assert response.count(b"HTTP/1.1 201 Created") == 1
    assert response.count(b"HTTP/1.1 200 OK") == 1
    assert b"201 Created" in response
    assert b"200 OK" in response
    assert b"User created" in response
    assert b"This is the about page" in response


def test_malformed_chunk_size_returns_400():
    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        b"ZZZ\r\n"
        b"hello\r\n"
        b"0\r\n\r\n"
    )

    response = run_server_request(request)

    assert b"400" in response


def test_missing_chunk_data_delimiter_returns_400():
    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Transfer-Encoding: chunked\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        b"5\r\n"
        b"hello"
        b"XX"
        b"0\r\n\r\n"
    )

    response = run_server_request(request)

    assert b"400" in response


def test_chunked_body_exceeding_limit_returns_413():
    config = ServerConfig(
        socket_timeout=2,
        max_body_size=10,
    )

    request = make_chunked_request([
        b"123456",
        b"78901",
    ])

    response = run_server_request(
        request,
        config=config,
    )

    assert b"413" in response
