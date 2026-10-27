class ServerConfig:
    def __init__(self, socket_timeout=5.0, max_header_size=8192, max_body_size=512 *1024 ):
        self.socket_timeout = socket_timeout
        self.max_header_size = max_header_size
        self.max_body_size = max_body_size
        self.header_delimiter = b"\r\n\r\n"