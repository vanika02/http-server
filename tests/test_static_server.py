
import socket
import threading

from config import ServerConfig
from server import handle_client


def receive_response(sock):
    """Read one complete HTTP response using Content-Length."""

    received = bytearray()

    while b"\r\n\r\n" not in received:
        chunk = sock.recv(4096)

        if not chunk:
            raise ConnectionError("Connection closed before response headers")

        received.extend(chunk)

    header_bytes, body = received.split(b"\r\n\r\n", 1)

    lines = header_bytes.decode("iso-8859-1").split("\r\n")
    status_line = lines[0]

    headers = {}

    for line in lines[1:]:
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()

    content_length = int(headers["content-length"])

    while len(body) < content_length:
        chunk = sock.recv(4096)

        if not chunk:
            raise ConnectionError("Connection closed before complete body")

        body.extend(chunk)

    return status_line, headers, bytes(body[:content_length])


def make_request(static_root, request_path):
    """Send a request through the actual HTTP server handler."""

    server_socket, client_socket = socket.socketpair()

    config = ServerConfig(
        socket_timeout=2,
        static_root=static_root,
    )

    server_thread = threading.Thread(
        target=handle_client,
        args=(server_socket, config),
    )

    server_thread.start()

    try:
        request = (
            f"GET {request_path} HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("ascii")

        client_socket.sendall(request)

        return receive_response(client_socket)

    finally:
        client_socket.close()
        server_thread.join(timeout=3)

        assert not server_thread.is_alive()


def test_static_text_file_through_http_server(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    expected = b"Hello from the custom HTTP server!"
    (static_root / "hello.txt").write_bytes(expected)

    status, headers, body = make_request(
        static_root,
        "/static/hello.txt",
    )

    assert status == "HTTP/1.1 200 OK"
    assert headers["content-type"] == "text/plain"
    assert headers["content-length"] == str(len(expected))
    assert headers["connection"] == "close"
    assert body == expected


def test_static_binary_file_through_http_server(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    expected = bytes([0, 255, 128, 10, 65, 0, 34])
    (static_root / "image.png").write_bytes(expected)

    status, headers, body = make_request(
        static_root,
        "/static/image.png",
    )

    assert status == "HTTP/1.1 200 OK"
    assert headers["content-type"] == "image/png"
    assert headers["content-length"] == str(len(expected))
    assert body == expected


def test_missing_static_file_through_http_server(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    status, headers, body = make_request(
        static_root,
        "/static/missing.txt",
    )

    assert status == "HTTP/1.1 404 Not Found"
    assert body == b"404 Not Found"
