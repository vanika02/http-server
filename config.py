class ServerConfig:
    def __init__(self):
        self.socket_timeout = 5.0
        self.max_header_size = 16 * 1024
        self.max_body_size = 1 * 1024 * 1024