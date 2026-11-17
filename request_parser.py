import re 

from exceptions import HTTPParseError

METHOD_TOKEN_PATTERN = re.compile(
    rb"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$"
)

SUPPORTED_HTTP_VERSIONS = {
    b"HTTP/1.0",
    b"HTTP/1.1"
}

class HTTPRequest:
    """
    A Parsed HTTP request.

    Attributes:
        headers (dict): Dictionary of HTTP headers.
        body (bytes): Raw Request body. Empty of request is None.
        method (str): HTTP method (GET, POST, etc.)
        path (str): Requested path
        http_version (str): HTTP version
    """

    def __init__(
        self,
        method: str,
        path: str,
        http_version: str,
        headers: dict[str, str],
        body: bytes,
    ):
        """
        Initialize an HTTPRequest object.

        Args: 
            method (str): HTTP method.
            path (str): Requested path.
            http_version (str): HTTP version string.
            headers (dict[str, str]): Parsed headers with lowercase keys.
            body (bytes): Raw request body.
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
        
def parse_request_head(header_bytes: bytes):
    header_lines = header_bytes.split(b"\r\n")

    if not header_lines or not header_lines[0]:
        raise HTTPParseError(
            "Empty request"
        )
    
    request_line = header_lines[0]

    if request_line.count(b" ") != 2:
        raise HTTPParseError("Malformed request line")
    
    method_bytes, path_bytes, version_bytes = request_line.split(b" ")

    if not method_bytes or not path_bytes or not version_bytes:
        raise HTTPParseError("Malformed request line")

    if not METHOD_TOKEN_PATTERN.fullmatch(method_bytes):
        raise HTTPParseError("Invalid HTTP method")

    if version_bytes not in SUPPORTED_HTTP_VERSIONS:
        raise HTTPParseError("Unsupported HTTP version")

    if any(byte <= 32 or byte == 127 for byte in path_bytes):
        raise HTTPParseError("Invalid request target")
    
    try:
        method = method_bytes.decode("ascii")
        path = path_bytes.decode("ascii")
        http_version = version_bytes.decode("ascii")

    except UnicodeDecodeError as exc:
        raise HTTPParseError(
            "Invalid request encoding"
        ) from exc 
    
    headers = {}
    content_lengths = []

    for line in header_lines[1:]:

        if not line:
            continue

        if b":" not in line:
            raise HTTPParseError(
                "Malformed header"
            )
        key_bytes, value_bytes = line.split(b":", 1)

        try:
            key = key_bytes.decode("ascii").lower()
            value = value_bytes.strip().decode("ascii")
        except UnicodeDecodeError as exc:
            raise HTTPParseError(
                "Invlid header encoding"
            ) from exc 
        
        if not key:
            raise HTTPParseError("Empty header name")
            
        headers[key] = value

        if key == "content-length":
            try:
                length = int(value)
            except ValueError as exc:
                raise HTTPParseError(
                    "Invalid Content-Length"
                ) from exc 
            
            if length < 0:
                raise HTTPParseError(
                    "Content-Length cannot be negative"
                )
            
            content_lengths.append(length)

    if len(content_lengths) > 1:
        raise HTTPParseError(
            "Duplicate Content-Length"
        )
    
    content_length = (
        content_lengths[0]
        if content_lengths
        else 0
    )

    return (
        method,
        path,
        http_version,
        headers,
        content_length
    )