from exceptions import HTTPParseError

class HTTPRequest:
    """
    A class representing an HTTP request.

    Attributes:
        headers (dict): Dictionary of HTTP headers.
        body (bytes): Request body.
        method (str): HTTP method (GET, POST, etc.)
        path (str): Requested path
        http_version (str): HTTP version
    """

    def __init__(
        self,
        method: str,
        path: str,
        http_version: str,
        headers: dict[str, str]
        body: bytes,
    ):
        """
        Initialize an HTTPRequest object.

        Args: 
            raw_request (bytes): Raw HTTP request string.
        """

        self.method = method
        self.path = path
        self.http_version = http_version
        self.headers = headers
        self.body = body

    def __repr__(self):
        """Return a short summary (body omitted to keep logs readable)."""
        return (
            f"HTTPRequest("
            f"method={self.method}, "
            f"path={self.path}, "
            f"headers={len(self.headers)})"
        )
        