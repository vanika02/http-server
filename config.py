from dataclasses import dataclass

@dataclass(frozen=True)
class ServerConfig:
    def __init__(self, socket_timeout=5.0, max_header_size=16 * 1024, max_body_size=1 * 1024 * 1024):
        self.socket_timeout = socket_timeout
        self.max_header_size = max_header_size
        self.max_body_size = max_body_size
        self.header_delimiter = b"\r\n\r\n"

        def __post_init__(self):
            if self.socket_timeout <= 0:
                raise ValueError("socket_timeout must be positive")
            
            if self.max_header_size <= 0:
                raise ValueError("max_header_size must be positive")

            if self.max_body_size < 0:
                raise ValueError("max_body_size cannot be negative")

            if not self.header_delimiter:
                raise ValueError("header_delimiter cannot be empty")