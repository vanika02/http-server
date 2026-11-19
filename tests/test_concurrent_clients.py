import socket
import threading

from server import handle_client
from config import ServerConfig

def test_multiple_clients_can_connect_concurrently():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(10)

    host, port = server.getsockname()
    config = ServerConfig()

    server_thread = threading.Thread(
        target=lambda: [
            handle_client(server.accept()[0], config)
            for _ in range(5)
        ],
        daemon=True 
    )
    server_thread.start()

    responses = []
    errors = []

    def make_request():
        try:
            with socket.create_connection((host, port)) as client:
                client.sendall(
                    b"GET / HTTP/1.1\r\n"
                    b"Host: localhost\r\n"
                    b"Connection: close\r\n"
                    b"\r\n"
                )

                response = client.recv(4096)
                responses.append(response)
        
        except Exception as exc:
            errors.append(response)
    
    clients = [
        threading.Thread(target=make_request)
        for _ in range(5)
    ]

    try:
        for client in clients:
            client.start()
        
        for client in clients:
            client.join(timeout=3)

        assert not errors
        assert all(not client.is_alive() for client in clients)
        assert len(responses) == 5
        assert all(
            response.startswith(b"HTTP/1.1 200 OK")
            for response in responses
        )
    
    finally:
        server.close()