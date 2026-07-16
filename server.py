import socket
import json
from router import route
from request_parser import HTTPRequest

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
    
    # seperate the header section from any early body data
    header_bytes, body_buffer = header_buffer.split(b"\r\n\r\n", 1)
    header_text = header_bytes.decode("utf-8", errors="ignore")

    # extract content-length value using regex
    match = re.search(r"Content-Length:\s*(\d+)", header_text, re.IGNORECASE)
    if not match:
        raise ValueError("Content-Length header is not found in the protocol.")
    
    content_length = int(match.group(1))

    # read the remaining body data based on the content-length
    remaining_bytes = content_length - len(body_buffer)

    while remaining_bytes > 0:
        chunk = sock.recv(min(4096, remaining_bytes))
        if not chunk:
            raise ConnectionError("Socket closed before full content was read.")
        body_buffer.extend(chunk)
        remaining_bytes -= len(chunk)
    
    return bytes(body_buffer)

while True:
    client_socket, client_address = server_socket.accept()

    request = _read_until_content_length(client_socket)

    # print("RAW REQUEST:")
    # print(repr(request))


    if not request:
        client_socket.close()
        continue

    print(request)


    # parse request
    parsed_req = 
    # request_line = request.split('\n')[0]
    # method, path, version = request_line.split()


    # parts = request.split("\r\n\r\n", 1)
    # body = ""
    
    # if len(parts) > 1:
    #     body = parts[1].strip()

    # status, content_type, response_body = route(method, path, body)
    
    # print("Method: ", method)
    # print("Path: ", path)
    # print("Body=", repr(body))


    response = (
        f"HTTP/1.1 {status}\n"
        f"Content-Type: {content_type}\n\n"
        f"{response_body}"
    )

    client_socket.send(response.encode())
    client_socket.close()