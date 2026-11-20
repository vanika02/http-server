import socket 
import threading

from config import ServerConfig
from server import _client_worker, run_server

def test_client_worker_removes_itself_after_disconnect():
    server_socket, client_socket = socket.socketpair()

    workers = set()
    client_sockets = {}
    workers_lock = threading.Lock()

    config = ServerConfig()

    worker = threading.Thread(
        target=_client_worker,
        args=(
            server_socket,
            config,
            workers,
            client_sockets,
            workers_lock,
        ),
    )

    with workers_lock:
        workers.add(worker)
        client_sockets[worker] = server_socket

    worker.start()

    client_socket.close()

    worker.join(timeout=2)

    assert not worker.is_alive()

    with workers_lock:
        assert worker not in workers
        assert worker not in client_sockets
    
    server_socket.close()

def test_run_server_shuts_down_with_active_clients():

    temporary_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    temporary_socket.bind(("127.0.0.1", 0))
    port = temporary_socket.getsockname()[1]
    temporary_socket.close()

    shutdown_event = threading.Event()

    server_thread = threading.Thread(
        target=run_server,
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "shutdown_event": shutdown_event,
        },
    )

    server_thread.start()

    clients = []

    try:

        for _ in range(3):
            client = socket.create_connection(
                ("127.0.0.1", port),
                timeout=2
            )

            clients.append(client)

        shutdown_event.set()

        server_thread.join(timeout=5)

        assert not server_thread.is_alive(), (
            "Server did not terminate after shutdown"
        )

    finally:
        shutdown_event.set()

        for client in clients:
            client.close()
        
        server_thread.join(timeout=5)
    
    assert not server_thread.is_alive()