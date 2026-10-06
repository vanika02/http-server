import socket
import threading

from server import handle_client

def test_two_requests_on_same_connection():

    server_socket, client_socket = socket.socketpair()

    server_thread = threading.Thread(
        target=handle_client,
        args=(server_socket,)
    )

    server_thread.start()

    request1 = (
        b"GET / HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
    )

    request2 = (
        b"GET /about HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )
    
    client_socket.sendall(request1)

    response1 = client_socket.recv(4096)

    assert b"HTTP/1.1 200 OK" in response1
    assert b"Hello Dharampal" in response1
    assert b"Connection: keep-alive" in response1 

    client_socket.sendall(request2)

    response2 = client_socket.recv(4096)

    assert b"HTTP/1.1 200 OK" in response2
    assert b"About Your Mom" in response2
    assert b"Connection: close" in response2

    client_socket.close()

    server_thread.join(timeout=1)

    assert not server_thread.is_alive()

def test_malformed_request_returns_400():

    server_socket, client_socket = socket.socketpair()

    server_thread = threading.Tread(
        target=handle_client,
        args=(server_socket,)
    )

    server_thread.start()

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: abc\r\n"
        b"\r\n"
    )

    client_socket.sendall(request)

    response = client_socket.recv(4096)

    assert b"HTTP/1.1 400 Bad Request" in response
    assert b"Connection: close" in response
    assert b"Bad Request" in response

    client_socket.close()

    server_thread.join(timeout=1)

    assert not server_thread.is_alive()