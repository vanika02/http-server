import socket

from router import route
from request_parser import HTTPRequest
from http_response import HTTPResponse


HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"server running on http://{HOST}:{PORT}")


def _read_until_content_length(sock, buffer) -> bytes:

    """Read and extract exactly one HTTP request."""

    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(4096)

        if not chunk:
            raise ConnectionError(
                "Socket closed while reading headers."
            )

        buffer.extend(chunk)
    
    # seperate the header section from any early body data
    header_bytes, remaining = buffer.split(b"\r\n\r\n", 1)
    remaining = bytearray(remaining)

    header_text = header_bytes.decode()

    content_length = 0

    for line in header_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break
    
    while len(remaining) < content_length:
        chunk = sock.recv(4096)

        if not chunk:
            break 
        remaining.extend(chunk)
    
    request_body = remaining[:content_length]
    leftover = remaining[content_length:]

    raw_request = (
        header_bytes
        + b"\r\n\r\n"
        + request_body
    )

    buffer.clear()
    buffer.extend(leftover)

    return raw_request

while True:
    client_socket, client_address = server_socket.accept()


    try: 
        buffer = bytearray()
        raw_request = _read_until_content_length(client_socket, buffer)
        if not raw_request:
            continue 
        
        request = HTTPRequest(raw_request)

        print("Method:", request.method)
        print("Path:", request.path)
        print("Expected body length:", 50000)
        print("Actual parsed body length:", len(request.body))
        print("Content-Length header:", request.headers.get("content-length"))

        method = request.method
        path = request.path
        body = request.body

        status, content_type, response_body = route(
            method, path, body
        )

        response = HTTPResponse(
            status_code=status,
            body=response_body,
            headers={
                "Content-Type": content_type,
                "Connection": "close"
            },
        )

        client_socket.sendall(response.build())

    finally:
        client_socket.close()