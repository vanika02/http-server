import socket

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(1)

print(f"Server running on http://{HOST}/{PORT}")

while True:
    client_socket, client_address = server_socket.accept()

    request = client_socket.recv(1024).decode()
    print(request)

    response = "HTTP/1.1 200 OK\n\nHello World"

    client_socket.send(response.encode())

    client_socket.close()