from dataclasses import dataclass, field 
from pathlib import Path 

@dataclass(frozen=True)
class ServerConfig:
        socket_timeout: float = 5.0
        max_header_size: int = 16 * 1024
        max_body_size: int = 1 * 1024 * 1024
        header_delimiter: bytes = b"\r\n\r\n"

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

            object.__setattr__(
                self, 
                "static_root",
                Path(self.static_root).resolve()
            )