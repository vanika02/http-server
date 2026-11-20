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