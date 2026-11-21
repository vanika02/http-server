# Building an HTTP Server from Scratch in Python
 
A lightweight HTTP server implemented from scratch using Python TCP sockets. The project explores how web servers handle network connections, parse HTTP requests, route requests, and construct responses without relying on a web framework.
 
The goal was to understand the mechanisms that frameworks such as Flask and FastAPI abstract away.
 
## Features
 
### HTTP Request Handling
- Accepts TCP connections using Python's `socket` module.
- Parses HTTP request lines and headers.
- Handles partial TCP reads and request bodies using `Content-Length`.
- Preserves unread bytes to support multiple requests received over the same connection.
- Validates request structure, headers, HTTP versions, and content length.
- Rejects unsupported `Transfer-Encoding` requests.

### HTTP Response Handling
- Builds HTTP responses with status codes, headers, and response bodies.
- Generates `Content-Length`, `Content-Type`, `Date`, and `Server` headers where appropriate.
- Handles responses with no body, including `204 No Content`.
- Returns appropriate error responses for malformed requests and oversized requests.

### Routing and Application Logic
Supports the following routes:
 
| Method | Path | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/about` | About page |
| GET | `/api` | JSON API response |
| POST | `/signup` | Register a user |
| POST | `/login` | Validate user credentials |
 
- Distinguishes between `404 Not Found` and `405 Method Not Allowed`.
- Returns an `Allow` header for unsupported methods on known routes.
- Validates JSON request bodies.
- Uses in-memory storage for user data.

### Connection and Concurrency Management
- Supports persistent HTTP/1.1 connections.
- Handles multiple requests over a single connection.
- Uses a thread-per-client model to handle concurrent connections.
- Protects shared user data using thread synchronization.
- Implements configurable socket timeouts and request size limits.
- Tracks active client workers and supports graceful server shutdown.

## Architecture
 
The project is divided into modules, with each module responsible for a specific part of the server.
 
```text
http-server/
├── server.py
├── request_parser.py
├── http_response.py
├── router.py
├── handlers.py
├── config.py
├── exceptions.py
├── requirements.txt
├── tests/
│   ├── test_concurrent_clients.py
│   ├── test_config.py
│   ├── test_handlers.py
│   ├── test_http_response.py
│   ├── test_persistent_connection.py
│   ├── test_request_framing.py
│   ├── test_request_parser.py
│   ├── test_router.py
│   └── test_server_lifecycle.py
└── README.md
```
 
| Module | Responsibility |
|---|---|
| `server.py` | TCP socket management, client workers, request processing, and server lifecycle |
| `request_parser.py` | HTTP request-line, header, and request validation |
| `http_response.py` | HTTP response construction and serialization |
| `router.py` | URL routing and HTTP method handling |
| `handlers.py` | Application logic for home, API, signup, and login routes |
| `config.py` | Server configuration and request limits |
| `exceptions.py` | Custom exceptions for parsing, size limits, and timeouts |
 
## Request Lifecycle
 
1. The server creates a TCP socket, binds it to a host and port, and starts listening.
2. When a client connects, the server creates a dedicated worker thread.
3. The worker reads bytes from the socket and identifies the HTTP request boundary.
4. The request parser validates the request line and headers.
5. The server reads the request body according to `Content-Length`.
6. The router matches the request method and path.
7. The selected handler processes the request.
8. The response builder serializes the HTTP response into bytes.
9. The server sends the response and either waits for another request or closes the connection.
## Requirements
 
- Python 3.10+
- pytest for running tests
## Setup and Usage
 
Clone the repository:
 
```bash
git clone <repository-url>
cd http-server
```
 
Create and activate a virtual environment:
 
```bash
python3 -m venv venv
source venv/bin/activate
```
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
Start the server:
 
```bash
python3 server.py
```
 
The server listens at:
 
```text
http://127.0.0.1:8080
```
 
## Example Requests
 
### GET request
 
```bash
curl -i http://127.0.0.1:8080/
```
 
### GET JSON API
 
```bash
curl -i http://127.0.0.1:8080/api
```
 
### Signup
 
```bash
curl -i -X POST http://127.0.0.1:8080/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"Rani","password":"1234"}'
```
 
### Login
 
```bash
curl -i -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Rani","password":"1234"}'
```
 
## Running Tests
 
Run the complete test suite:
 
```bash
pytest -q
```
 
The test suite covers:
 
- HTTP request parsing and validation.
- Request framing and partial TCP reads.
- Persistent connections.
- HTTP response serialization.
- Routing and status codes.
- Handler validation and user operations.
- Concurrent client handling.
- Server configuration.
- Server startup and shutdown lifecycle.
**Latest verified result:** 82 tests passed.
 
## Scope and Limitations
 
This project implements a subset of HTTP/1.1 for learning purposes. It is not a fully compliant or production-ready HTTP server.
 
Current limitations include:
 
- Chunked transfer encoding is not supported.
- HTTPS/TLS is not implemented.
- User data is stored in memory and is lost when the server restarts.
- Passwords are stored as plaintext; the authentication handlers are demonstrative, not suitable for real applications.
- The server does not implement a complete HTTP feature set or production-grade authentication and security controls.

## Key Learning Outcomes
 
Building this server provided practical experience with:
 
- TCP sockets and client-server communication.
- HTTP request and response structure.
- TCP stream framing and partial reads.
- HTTP request parsing and validation.
- Persistent connections and connection lifecycle management.
- Thread-based concurrency and shared-state synchronization.
- Modular backend architecture.
- Automated testing of network-facing components.
The project helped build an understanding of backend server internals by implementing the core request-response lifecycle rather than relying entirely on a web framework.
 