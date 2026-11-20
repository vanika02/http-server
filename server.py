import threading
import socket

from router import route
from request_parser import HTTPRequest, parse_request_head
from http_response import HTTPResponse
from exceptions import HTTPParseError, HTTPRequestTooLarge, HeaderReadTimeout, BodyReadTimeout
from config import ServerConfig


HOST = '127.0.0.1'
PORT = 8080

def _read_one_request(sock, buffer, config):

    """Read and extract exactly one HTTP request."""
    
    while True:

        try:
            header_end = buffer.find(config.header_delimiter)

            if header_end != -1:
                # the delimiter marks the end of the header block
                if header_end > config.max_header_size:
                    raise HTTPRequestTooLarge("Request headers are too large")

                header_bytes = bytes(buffer[:header_end])
                remaining = bytearray(buffer[header_end + len(config.header_delimiter):])
                break 

            if len(buffer) > config.max_header_size:
                raise HTTPRequestTooLarge(
                    "Request headers are too large"
                )
        
            chunk = sock.recv(4096)

            if not chunk:
                if not buffer:
                    return None 

                raise ConnectionError(
                    "Socket closed while reading headers."
                )

            buffer.extend(chunk)

        except TimeoutError as exc:
            raise HeaderReadTimeout(
                "Request header timeout"
            ) from exc
        
    (
        method,
        path,
        http_version,
        headers,
        content_length,
    ) = parse_request_head(header_bytes)

    try:
        
        if content_length is None:
            content_length = 0

        if content_length > config.max_body_size:
            raise HTTPRequestTooLarge(
                "Request body is too large"
            )
        
        
        while len(remaining) < content_length:
            chunk = sock.recv(4096)

            if not chunk:
                raise ConnectionError(
                    "Socket closed before complete request body."
                )

            remaining.extend(chunk)
        
        request_body = bytes(remaining[:content_length])
        leftover = remaining[content_length:]

        raw_request = (
            header_bytes
            + b"\r\n\r\n"
            + request_body
        )

        buffer.clear()
        buffer.extend(leftover)

    except TimeoutError as exc: 
        raise BodyReadTimeout(
            "Request body timeout"
        ) from exc 

    return (
        raw_request,
        method,
        path,
        http_version,
        headers,
        request_body
    )

def _client_worker(
    client_socket,
    config,
    workers,
    client_sockets,
    workers_lock
):
    """Run one client handler and clean up its tracking state."""

    current_thread = threading.current_thread()

    try:
        handle_client(client_socket, config)
    
    except (ConnectionError, OSError):
        pass 
    
    finally:
        with workers_lock:
            workers.discard(current_thread)
            client_sockets.pop(current_thread, None)

def _shutdown_server(
    server_socket,
    shutdown_event,
    workers,
    client_sockets,
    workers_lock
):
    """Stop accepting connections and terminate active client workers."""

    shutdown_event.set()
    server_socket.close()

    with workers_lock:
        active_workers = list(workers)
        active_sockets = list(client_sockets.values())

    for client_socket in active_sockets:
        try:
            client_socket.shutdown(socket.SHUT.RDWR)
        except OSError:
            pass 
        
        try:
            client_socket.close()
        except OSError:
            pass 
        
    for worker in active_workers:
        worker.join(timeout=3)

    still_running = [
        worker.name 
        for worker in active_workers
        if worker.is_alive()
    ]

    if still_running:
        print("Warning: workers still running:", still_running)
    
    print("Server shutdown complete")

def run_server(host=HOST, port=PORT):

    config = ServerConfig()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SQL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))
    server_socket.listen(10)

    workers = set()
    client_sockets = {}
    workers_lock = threading.Lock()

    print(f"server running on http://{HOST}:{PORT}")

    try:
        while not shutdown_event.is_set():

            try:
                client_socket, client_address = server_socket.accept()
            
            except OSError:
                if shutdown_event.is_set():
                    break
                raise 

            print(f"Connection from {client_address}")

            client_thread = threading.Thread(
                target=_client_worker,
                args=(
                    client_socket,
                    config,
                    workers,
                    client_sockets,
                    workers_lock
                ),
                daemon=False 
            )

            with workers_lock:
                workers.add(client_thread)
                client_sockets[client_thread] = client_socket
            
            try:
                client_thread.start()
            except Expection:
                with workers_lock:
                    workers.discard(client_thread)
                    client_sockets.pop(client_thread, None)
                
                client_socket.close()
                raise
    
    except KeyboardInterrupt:
        print("\nShutdown requested")

    finally:
        shutdown_event.set()
        server_socket.close()

        with workers_lock:
            active_workers = list(workers)
            active_sockets = list(client_sockets.values())
        
        for client_socket in active_sockets:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass 
            
            client_socket.close()

        for worker in active_workers:
            worker.join()

        print("Server shutdown complete")

def handle_client(client_socket, config):

    client_socket.settimeout(config.socket_timeout)

    buffer = bytearray()
    
    try: 
        while True:
            try:

                result = _read_one_request(
                    client_socket,
                    buffer,
                    config
                )
                
                if result is None:
                    break

                (
                    raw_request,
                    method,
                    path,
                    http_version,
                    headers,
                    body
                ) = result

                
            except HTTPParseError:
                response = HTTPResponse(
                    status_code=400,
                    body="Bad Request",
                    headers={
                        "Content-Type": "text/plain",
                        "Connection": "close"
                    },
                )

                client_socket.sendall(
                    response.build()
                )

                break

            except HTTPRequestTooLarge as error:
                message = str(error)

                status_code = (
                    431 if "headers" in message.lower()
                    else 413
                )

                response = HTTPResponse(
                    status_code=status_code,
                    body=message,
                    headers={
                        "Content-Type": "text/plain",
                        "Connection": "close",
                    }
                )

                client_socket.sendall(response.build())
                break 

            except (HeaderReadTimeout, BodyReadTimeout) as exc:
                print(f"Request timed out: {exc}")

                response = HTTPResponse(
                    status_code=408,
                    body="Request Timeout",
                    headers={
                        "Content-Type": "text/plain",
                        "Connection": "close",
                    },
                )

                client_socket.sendall(response.build())
                break
            request = HTTPRequest(
                method=method,
                path=path,
                http_version=http_version,
                headers=headers,
                body=body
            )

            connection = request.headers.get("connection", "").lower()

            print("DEBUG headers:", repr(request.headers))
            print("DEBUG version:", repr(request.http_version))
            print("DEBUG connection:", repr(connection))
            
            if request.http_version == "HTTP/1.1":
                should_close = connection == "close"
            else:
                should_close = connection != "keep-alive"

            print("Method:", request.method)
            print("Path:", request.path)
            print("Expected body length:", request.headers.get("content-length"))
            print("Actual parsed body length:", len(request.body))
            print("Content-Length header:", request.headers.get("content-length"))

            method = request.method
            path = request.path
            body = request.body

            status, content_type, response_body, extra_headers = route(
                method, path, body
            )
            
            response_headers = {
                "Content-Type": content_type,
                "Connection": "close" if should_close else "keep-alive"
            }

            response_headers.update(extra_headers)

            response = HTTPResponse(
                status_code=status,
                body=response_body,
                headers=response_headers
            )

            response_bytes = response.build()

            print("Sending response:", response_bytes[:100])
            
            client_socket.sendall(response_bytes)

            if should_close:
                break


    finally:
        client_socket.close()

if __name__ == "__main__":
    run_server()