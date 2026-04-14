import socket

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(1)

print(f"server running on http://{HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode()
    print(request)


    # parse request
    request_line = request.split('\n')[0]
    method, path, version = request_line.split()

    # routing
    if path == "/":
        body = "Hello vanika"
    elif path == "/about":
        body = "About page"
    elif path == "/api":
        body = "API Endpoints"
    else:
        body = "404 not found"

    print("Method: ", method)
    print("Path: ", path)

    response = "HTTP/1.1 200 OK\n\n{body}"

    client_socket.send(response.encode())

    client_socket.close()