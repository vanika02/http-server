# Building an HTTP Server from Scratch in Python

A lightweight HTTP/1.1 server implemented from scratch using Python TCP sockets.

This project explores how web servers accept network connections, parse HTTP requests, manage connection lifecycles, route requests and construct responses without relying on a web framework.

The goal was to understand the backend mechanisms that frameworks such as Flask and FastAPI abstract away.

[![Tests](https://github.com/vanika02/http-server/actions/workflows/tests.yml/badge.svg)](https://github.com/vanika02/http-server/actions/workflows/tests.yml)

## Features

### HTTP Request Handling

- Accepts TCP connections using Python's `socket` module.
- Parses HTTP request lines and headers.
- Handles partial TCP reads and request bodies using `Content-Length`.
- Supports chunked transfer encoding, including chunk extensions and trailers.
- Preserves unread bytes to support multiple requests received over the same connection.
- Validates request structure, headers, HTTP versions and request framing.
- Rejects malformed requests and conflicting `Content-Length` and `Transfer-Encoding` headers.
- Enforces configurable request header and body size limits.

### HTTP Response Handling

- Constructs HTTP responses with status codes, headers and response bodies.
- Generates `Content-Length`, `Content-Type`, `Date` and `Server` headers.
- Handles responses without bodies, including `204 No Content`.
- Supports `HEAD` requests without sending a response body.
- Returns appropriate error responses for malformed and oversized requests.

### Routing and Application Logic

| Method | Path | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/about` | About page |
| GET | `/api` | JSON API response |
| GET | `/health` | Health-check endpoint |
| POST | `/signup` | Register a user |
| POST | `/login` | Validate user credentials |

Additional capabilities:

- Distinguishes between `404 Not Found` and `405 Method Not Allowed`.
- Returns an `Allow` header for unsupported methods on known routes.
- Validates JSON request bodies.
- Uses in-memory user storage.
- Hashes passwords using salted `hashlib.scrypt`.
- Uses constant-time password comparison.

### Static File Serving

- Serves files from a configured static directory.
- Determines content types using MIME detection.
- Protects against path traversal attempts.
- Enforces a configurable maximum static-file size.
- Returns appropriate errors for missing, inaccessible and oversized files.

### Connection and Concurrency Management

- Supports persistent HTTP/1.1 connections.
- Handles multiple requests over a single connection.
- Uses a thread-per-client model.
- Limits the number of simultaneous client connections.
- Protects shared application state using thread synchronization.
- Implements configurable socket timeouts.
- Tracks active client workers and supports graceful server shutdown.

## Architecture

The project separates networking, HTTP parsing, response construction and application logic into independent modules.

```text
http-server/
├── server.py
├── request_parser.py
├── http_response.py
├── router.py
├── handlers.py
├── static_files.py
├── config.py
├── exceptions.py
├── static/
├── tests/
├── .github/
│   └── workflows/
│       └── tests.yml
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

| Module | Responsibility |
|---|---|
| `server.py` | TCP socket management, client workers, request processing and server lifecycle |
| `request_parser.py` | HTTP request parsing, validation and request-body framing |
| `http_response.py` | HTTP response construction and serialization |
| `router.py` | URL routing and HTTP method handling |
| `handlers.py` | Application logic for API, signup and login routes |
| `static_files.py` | Static-file resolution, validation and loading |
| `config.py` | Server configuration and resource limits |
| `exceptions.py` | Custom exceptions for parsing, size limits and timeouts |

## Request Lifecycle

1. The server creates a TCP socket, binds it to a host and port, and starts listening.
2. When a client connects, the server checks available connection capacity.
3. An available connection is assigned to a dedicated worker thread.
4. The worker reads bytes from the socket and identifies HTTP message boundaries.
5. The request parser validates the request line and headers.
6. The server reads the request body using `Content-Length` or chunked transfer encoding.
7. The router matches the request method and path.
8. The selected handler processes the request.
9. The response builder serializes the HTTP response into bytes.
10. The server sends the response and either waits for another request or closes the connection.

## Requirements

- Python 3.12+
- Docker (optional)
- pytest for running tests

The server itself uses Python's standard library and has no third-party runtime dependencies.

## Local Setup and Usage

Clone the repository:

```bash
git clone https://github.com/vanika02/http-server.git
cd http-server
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Start the server:

```bash
python server.py
```

By default, the server listens at:

```text
http://127.0.0.1:8080
```

The host and port can be configured using environment variables:

```bash
HOST=127.0.0.1 PORT=8080 python server.py
```

## Example Requests

### Health check

```bash
curl -i http://127.0.0.1:8080/health
```

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

## Docker

Build the Docker image:

```bash
docker build -t vanika-http-server .
```

Run the container:

```bash
docker run -d \
  --name http-server \
  -p 8080:8080 \
  vanika-http-server
```

Check the health endpoint:

```bash
curl -i http://localhost:8080/health
```

Inspect container logs:

```bash
docker logs http-server
```

The container runs as a non-root user and exposes port `8080`.

## Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the complete test suite:

```bash
pytest -q
```

The test suite covers:

- HTTP request parsing and validation.
- Partial TCP reads and request framing.
- Chunked transfer encoding.
- Persistent connections.
- HTTP response serialization.
- Routing and status codes.
- Static-file serving and path traversal protection.
- Handler validation and password hashing.
- Concurrent client handling and connection limits.
- Server configuration.
- Server startup and graceful shutdown.

**Latest verified result: 175 tests passed.**

### Continuous Integration

GitHub Actions automatically runs the test suite on pushes and pull requests targeting `main` or `master`.

Workflow:

```text
.github/workflows/tests.yml
```

## Scope and Limitations

This project implements a subset of HTTP/1.1 for educational purposes. It is not a fully compliant or production-ready HTTP server.

Current limitations include:

- HTTPS/TLS is not implemented directly. A reverse proxy or hosting platform is needed for HTTPS deployment.
- User data is stored in memory and is lost when the server restarts.
- The server uses a thread-per-client architecture rather than an asynchronous event loop.
- Static files are loaded fully into memory after passing the configured size check.
- Authentication is demonstrative and does not include production features such as persistent user storage, sessions, rate limiting or account recovery.
- The implementation does not cover the complete HTTP/1.1 specification.

## Key Learning Outcomes

Building this server provided practical experience with:

- TCP sockets and client-server communication.
- HTTP request and response structure.
- TCP stream framing and partial reads.
- Content-Length and chunked transfer encoding.
- Persistent connections and connection lifecycle management.
- Thread-based concurrency and shared-state synchronization.
- Resource limits and graceful shutdown.
- Static-file handling and path traversal protection.
- Modular backend architecture.
- Automated testing of network-facing components.
- Containerization with Docker and continuous integration with GitHub Actions.

The project helped build an understanding of backend server internals by implementing the request-response lifecycle rather than relying entirely on a web framework.