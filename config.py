from dataclasses import dataclass, field 
from pathlib import Path 

@dataclass(frozen=True)
class ServerConfig:
        socket_timeout: float = 5.0
        max_header_size: int = 16 * 1024
        max_body_size: int = 1 * 1024 * 1024
        header_delimiter: bytes = b"\r\n\r\n"
        max_connections: int = 50
        max_static_file_size: int = 5 * 1024 * 1024

        static_root: Path = field(
            default_factory=lambda: Path(__file__).resolve().parent / "static"
        )

        def __post_init__(self):
            if self.socket_timeout <= 0:
                raise ValueError("socket_timeout must be positive")
            
            if self.max_header_size <= 0:
                raise ValueError("max_header_size must be positive")

            if self.max_body_size < 0:
                raise ValueError("max_body_size cannot be negative")

            if not self.header_delimiter:
                raise ValueError("header_delimiter cannot be empty")
            
            if self.max_connections <= 0:
                raise ValueError("max_connections must be greater than 0")
            
            if self.max_static_file_size < 0:
                raise ValueError("max_statix_file_size cannot be negative")

            object.__setattr__(
                self, 
                "static_root",
                Path(self.static_root).resolve()
            )