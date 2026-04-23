# Build Your Own HTTP Server in Python

A lightwieght HTTP server from scratch using Python sockets to understand how web server works internally.

## Why Build this

I wanted to understand what frameworks like Flask and FastPI abstract away, including:

- TCP socket
- HTTP request/response lifecyle
- Routing
- JSON APIs
- POST request handling
- Basic server architecture

## Features

- Handles raw TCP socket connections
- Parses HTTP requests
- Supports GET routes:
    - /
    - /about
    - /api

- Supports POST requests
    - /signup
    - /login

- Returs JSON responses
- Modular architecture using seperate files
- Basic in-memory user storage

## Tech Stack
- Python 3 
- socket module
- json module

## Project Structure 

 ```
http-server/ 
├── server.py
├── router.py 
├── handlers.py 
└── README.md
```

## How to run

```
python3 server.py
```

## Then open
```
http://localhost:8080
```

## Example Requests

### GET
```
curl http://localhost:8080/api
```

### Signup
```
curl -X POST http://localhost:8080/signup \
-H "Content-Type: application/json" \
-d '{"username":"name","password":"password"}'
```
### Login
```
curl -X POST http://localhost:8080/login \
-H "Content-Type: application/json" \
-d '{"username":"name","password":"password"}'
```

## Concepts Learned
- HTTP protocol basics
- Request parsing
- Status codes
- Content-Type headers
- Routing systems
- Authentication flow basics
- Debugging raw network requests
- Future Improvements
- Multi-threaded request handling
- Persistent database storage
- Password hashing
- JWT authentication
- Static file serving
- Better HTTP compliance


## Key Learning Outcome

Building this project helped me understand how backend frameworks operate internally instead of only consuming abstractions.