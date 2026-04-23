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

