import socket
import json
from router import route

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"server running on http://{HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode()

    if not request:
        client_socket.close()
        continue

    print(request)


    # parse request
    request_line = request.split('\n')[0]
    method, path, version = request_line.split()


    parts = request.split("\n\n")
    body = ""
    
    if len(parts) > 1:
        body = parts[1].strip()

    status, content_type, response_body = route(method, path, body)

    # print("Method: ", method)
    # print("Path: ", path)

    response = (
        f"HTTP/1.1 {status}\n"
        f"Content-Type: {content_type}\n\n"
        f"{response_body}"
    )

    client_socket.send(response.encode())
    client_socket.close()