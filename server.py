import socket

from router import route
from request_parser import HTTPRequest, parse_request_head
from http_response import HTTPResponse
from exceptions import HTTPParseError

HOST = '127.0.0.1'
PORT = 8080


def _read_one_request(sock, buffer):

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
    
    (
        method,
        path,
        http_version,
        headers,
        content_length,
    ) = parse_request_head(header_bytes)
    
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

    return (
        raw_request,
        method,
        path,
        http_version,
        headers,
        request_body
    )

def run_server(host=HOST, port=PORT):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"server running on http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket)

def handle_client(client_socket):

    buffer = bytearray()
    
    try: 
        while True:

            try:

                result = _read_one_request(
                    client_socket,
                    buffer
                )
                
                if result is None:
                    break

                (
                    raw_request,
                    method,
                    path,
                    http_version,
                    headers,
                    body
                ) = result

                
            except HTTPParseError:
                response = HTTPResponse(
                    status_code=400,
                    body="Bad Request",
                    headers={
                        "Content-Type": "text/plain",
                        "Connection": "close"
                    },
                )

                client_socket.sendall(
                    response.build()
                )

                break

            request = HTTPRequest(
                method=method,
                path=path,
                http_version=http_version,
                headers=headers,
                body=body
            )

            connection = request.headers.get("connection", "").lower()

            print("DEBUG headers:", repr(request.headers))
            print("DEBUG version:", repr(request.http_version))
            print("DEBUG connection:", repr(connection))
            
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