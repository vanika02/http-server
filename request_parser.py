from exceptions import HTTPParseError

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

    if not header_lines:
        raise HTTPParseError(
            "Empty request"
        )
    
    request_line = header_lines[0].split()

    if len(request_line) != 3:
        raise HTTPParseError(
            "Malformed request line"
        )
    
    try:
        key = key.strip().decode().lower()
        method = request_line[0].decode()
        path = request_line[1].decode()
        http_version = request_line[2].decode()
    except UnicodeDecodeError as exc:
        raise HTTPParseError(
            "Invalid request encoding"
        ) from exc 
    

    headers[key] = value 
    
    headers = {}
    content_lengths = []

    for line in header_lines[1:]:

        if b":" not in line:
            raise HTTPParseError(
                "Malformed header"
            )
        key, value = line.split(b":", 1)

        try:
            key = key.strip().decode().lower()
            value = value.strip().decode()
        except UnicodeDecodeError as exc:
            raise HTTPParseError(
                "Invlid header encoding"
            ) from exc 
        
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