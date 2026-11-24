import socket 
import threading
import time 

from config import ServerConfig
from server import _client_worker, run_server
import server as server_module 

def test_client_worker_removes_itself_after_disconnect():
    server_socket, client_socket = socket.socketpair()

    workers = set()
    client_sockets = {}
    workers_lock = threading.Lock()

    config = ServerConfig()
    connection_slots = threading.BoundedSemaphore(
        config.max_connections
    )

    assert connection_slots.acquire(blocking=False)

    worker = threading.Thread(
        target=_client_worker,
        args=(
            server_socket,
            config,
            workers,
            client_sockets,
            workers_lock,
            connection_slots
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


def test_run_server_shuts_down_after_client_connections():

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

    clients = []

    try:
        server_thread.start()

        deadline = time.monotonic() + 5

        while time.monotonic() < deadline:
            try:
                client = socket.create_connection(
                    ("127.0.0.1", port),
                    timeout=2
                )
                clients.append(client)
                break

            except ConnectionRefusedError:
                time.sleep(0.05)

        assert clients, "Server did not start accepting connections"

        for _ in range(2):
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


def test_run_server_shuts_down_with_all_active_workers(monkeypatch):
    temporary_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    temporary_socket.bind(("127.0.0.1", 0))
    port = temporary_socket.getsockname()[1]
    temporary_socket.close()

    shutdown_event = threading.Event()

    worker_threads = []
    worker_threads_lock = threading.Lock()
    all_workers_started = threading.Event()

    original_worker = server_module._client_worker

    def tracked_worker(*args, **kwargs):
        current_thread = threading.current_thread()

        with worker_threads_lock:
            worker_threads.append(current_thread)

            if len(worker_threads) == 3:
                all_workers_started.set()

        original_worker(*args, **kwargs)

    monkeypatch.setattr(
        server_module,
        "_client_worker",
        tracked_worker,
    )

    server_thread = threading.Thread(
        target=server_module.run_server,
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "shutdown_event": shutdown_event,
        },
    )

    clients = []

    server_thread.start()

    try:
        deadline = time.monotonic() + 5

        while time.monotonic() < deadline:
            try:
                client = socket.create_connection(
                    ("127.0.0.1", port),
                    timeout=1,
                )
                clients.append(client)
                break

            except ConnectionRefusedError:
                time.sleep(0.01)

        assert clients, "Server did not start accepting connections"

        for _ in range(2):
            client = socket.create_connection(
                ("127.0.0.1", port),
                timeout=2,
            )
            clients.append(client)

        assert all_workers_started.wait(timeout=5), (
            "Not all client workers started"
        )

        shutdown_event.set()

        server_thread.join(timeout=5)

        assert not server_thread.is_alive(), (
            "Server thread did not terminate"
        )

        with worker_threads_lock:
            completed_workers = list(worker_threads)

        assert len(completed_workers) == 3

        assert all(
            not worker.is_alive()
            for worker in completed_workers
        ), "One or more client workers are still running"

    finally:
        shutdown_event.set()

        for client in clients:
            client.close()

        server_thread.join(timeout=5)

    assert not server_thread.is_alive()

def test_connection_capacity_is_released_after_disconnect(monkeypatch):
    temporary_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    temporary_socket.bind(("127.0.0.1", 0))
    port = temporary_socket.getsockname()[1]
    temporary_socket.close()

    shutdown_event = threading.Event()

    config = ServerConfig(
        max_connections=1,
        socket_timeout=5,
    )

    worker_threads = []
    worker_lock = threading.Lock()
    worker_started = threading.Event()

    original_worker = server_module._client_worker

    def tracked_worker(*args, **kwargs):
        current_thread = threading.current_thread()

        with worker_lock:
            worker_threads.append(current_thread)
            worker_started.set()

        original_worker(*args, **kwargs)

    monkeypatch.setattr(
        server_module,
        "_client_worker",
        tracked_worker,
    )

    server_thread = threading.Thread(
        target=run_server,
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "shutdown_event": shutdown_event,
            "config": config,
        },
    )

    clients = []

    def connect_with_retry():
        deadline = time.monotonic() + 5

        while time.monotonic() < deadline:
            try:
                client = socket.create_connection(
                    ("127.0.0.1", port),
                    timeout=2,
                )
                clients.append(client)
                return client

            except OSError:
                time.sleep(0.05)

        raise AssertionError("Server did not accept connections")

    try:
        server_thread.start()

        client_a = connect_with_retry()

        assert worker_started.wait(timeout=3), (
            "Worker for client A did not start"
        )

        with worker_lock:
            worker_a = worker_threads[0]

        client_b = connect_with_retry()
        client_b.settimeout(2)

        assert client_b.recv(1) == b"", (
            "Client B should have been rejected"
        )

        client_a.close()
        worker_a.join(timeout=3)

        assert not worker_a.is_alive(), (
            "Worker A did not terminate"
        )

        worker_started.clear()
        client_c = connect_with_retry()

        assert worker_started.wait(timeout=3), (
            "Worker for client C did not start"
        )

        with worker_lock:
            assert len(worker_threads) == 2

    finally:
        shutdown_event.set()

        for client in clients:
            client.close()

        server_thread.join(timeout=5)

    assert not server_thread.is_alive(), (
        "Server did not shut down cleanly"
    )