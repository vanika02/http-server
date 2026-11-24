import socket
import threading
import time

from server import run_server
from config import ServerConfig

def test_connection_limit_rejects_extra_connections():
    shutdown_event = threading.Event()

    config = ServerConfig(
        max_connections=1,
        socket_timeout=5,
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    port = server.getsockname()[1]
    server.close()

    server_thread = threading.Thread(
        target=run_server,
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "shutdown_event": shutdown_event,
            "config": config,
        },
    )

    server_thread.start()

    first_client = None
    second_client = None

    try:
        deadline = time.time() + 3

        while time.time() < deadline:
            try:
                first_client = socket.create_connection(
                    ("127.0.0.1", port),
                    timeout=1,
                )
                break
            except OSError:
                time.sleep(0.05)

        assert first_client is not None

        # Keep the first connection open without sending a request.
        # This occupies the only connection slot.
        second_client = socket.create_connection(
            ("127.0.0.1", port),
            timeout=2,
        )

        second_client.settimeout(2)

        assert second_client.recv(1) == b""

    finally:
        if first_client:
            first_client.close()

        if second_client:
            second_client.close()

        shutdown_event.set()
        server_thread.join(timeout=5)

    assert not server_thread.is_alive()