import socket

from router import route
from request_parser import HTTPRequest
from http_response import HTTPResponse
from exceptions import HTTPParseError

HOST = '127.0.0.1'
PORT = 8080


def _read_one_request(sock, buffer) -> bytes | None:

    """Read and extract exactly one HTTP request."""

    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(4096)

        if not chunk:
            if not buffer:
                return None 

            raise ConnectionError(
                "Socket closed while reading headers."
            )

        buffer.extend(chunk)
    
    header_bytes, remaining = buffer.split(
        b"\r\n\r\n",
        1
    )

    remaining = bytearray(remaining)

    header_text = header_bytes.decode()

    content_length = 0

    for line in header_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            value = line.split(":", 1)[1].strip()

            try:
                content_length = int(value)
            except ValueError as exc:
                raise HTTPParseError(
                    "Invalid Content-Length"
                ) from exc

            if content_length < 0:
                raise HTTPParseError(
                    "Content-Length cannot be negative"
                )
                
            break
    
    while len(remaining) < content_length:
        chunk = sock.recv(4096)

        if not chunk:
           raise ConnectionError(
            "Socket closed before complete request body."
           )
        remaining.extend(chunk)
    
    request_body = bytes(remaining[:content_length])
    leftover = remaining[content_length:]

    raw_request = (
        header_bytes
        + b"\r\n\r\n"
        + request_body
    )

    buffer.clear()
    buffer.extend(leftover)

    return raw_request

def run_server(host=HOST, port=PORT):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"server running on http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()

def handle_client(client_socket):

    buffer = bytearray()
    
    try: 
        while True:

            try:

                raw_request = _read_one_request(
                    client_socket,
                    buffer
                )

            except HTTPParseError:
                
                response = HTTPResponse(
                    status_code=400,
                    body="Bad Request",
                    headers={
                        "Content-Type": "test/plain",
                        "Connection": "close"
                    },
                )

                client_socket.sendall(
                    response.build()
                )

                break
            
            if raw_request is None:
                break

            request = HTTPRequest(raw_request)

            connection = request.headers.get("connection", "").lower()
            
            if request.http_version == "HTTP/1.1":
                should_close = connection == "close"
            else:
                should_close = connection != "keep-alive"

            print("Method:", request.method)
            print("Path:", request.path)
            print("Expected body length:", request.headers.get("content-length"))
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
                    "Connection": "close" if should_close else "keep-alive"
                },
            )

            print("Sending response:", response.build()[:100])
            client_socket.sendall(response.build())

            if should_close:
                break

    finally:
        client_socket.close()

if __name__ == "__main__":
    run_server()