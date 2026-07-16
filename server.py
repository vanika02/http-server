import socket
from router import route
from request_parser import HTTPRequest
import socket
import re

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"server running on http://{HOST}:{PORT}")


def _read_until_content_length(sock) -> bytes:

    """Extract body from POST request, Parse out the content-length value"""

    # read the header completly until the \r\n\r\n boundary
    header_buffer = bytearray()
    while b"\r\n\r\n" not in header_buffer:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Socket closed while reading headers.")
        header_buffer.extend(chunk)
    
    if not header_buffer:
        return ""
    
    # seperate the header section from any early body data
    header_bytes, body_buffer = header_buffer.split(b"\r\n\r\n", 1)
    header_text = header_bytes.decode()

    content_length = 0

    for line in header_text.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break
    
    while len(body) < content_length:
        chunk = sock.recv(4096)

        if not chunk:
            break 
        body.extend(chunk)
    
    raw_request = (
        header_bytes
        + b"\r\n\r\n"
        + body
    )

    return raw_request.decode(errors="ignore")


while True:
    client_socket, client_address = server_socket.accept()

    raw_request = _read_until_content_length(client_socket)

    # print("RAW REQUEST:")
    # print(repr(request))


    if not raw_request:
        client_socket.close()
        continue

    # print(raw_request)


    # parse request
    request = HTTPRequest(raw_request)

    # request_line = request.split('\n')[0]
    # method, path, version = request_line.split()

    method = request.method
    path = request.path
    headers = request.headers
    # parts = request.split("\r\n\r\n", 1)
    # body = ""
    
    # if len(parts) > 1:
    #     body = parts[1].strip()

    status, content_type, response_body = route(method, path, body)
    
    print("Method: ", method)
    print("Path: ", path)
    print("Body=", repr(body))


    response = (
        f"HTTP/1.1 {status}\n"
        f"Content-Type: {content_type}\n\n"
        f"{response_body}"
    )

    client_socket.send(response.encode())
    client_socket.close()