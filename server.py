import socket
import json

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

    # routing
    if path == "/":
        body = "Hello vanika"
        content_type = "text/plain"
        status = "200 ok"

    elif path == "/about":
        body = "About page"
        content_type = "text/plain"
        status = "200 ok"

    elif path == "/api":
        body = json.dumps({
            "name": "Vanika",
            "role": "Backroom anhilator"
        })
        content_type= "application/json"
        status = "200 ok"
    
    else:
        body = "404 not found"
        content_type = "text/plain"
        status = "404 Not Found"

    # print("Method: ", method)
    # print("Path: ", path)

    response = (
        
    )

    client_socket.send(response.encode())

    client_socket.close()