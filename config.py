class ServerConfig:
    def __init__(self, socket_timeout=5.0):
        self.socket_timeout = socket_timeout
        self.max_header_size = 16 * 1024
        self.max_body_size = 1 * 1024 * 1024
        self.header_delimiter = b"\r\n\r\n"