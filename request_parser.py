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
    """Parse and validate an HTTP request line and its headers."""

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
    transfer_encoding = False 
    host_count = 0

    for line in header_lines[1:]:

        if not line:
            continue

        if line.startswith((b" ", b"\t")):
            raise HTTPParseError("Folded headers are not supported")

        if b":" not in line:
            raise HTTPParseError(
                "Malformed header"
            )

        key_bytes, value_bytes = line.split(b":", 1)

        if not METHOD_TOKEN_PATTERN.fullmatch(key_bytes):
            raise HTTPParseError("Invalid header name")

        try:
            key = key_bytes.decode("ascii").lower()
            value = value_bytes.strip(b" \t").decode("ascii")
            
        except UnicodeDecodeError as exc:
            raise HTTPParseError(
                "Invlid header encoding"
            ) from exc 
        
        if any(
            (byte < 32 and byte != 9) or byte == 127
            for byte in value_bytes
        ):
            raise HTTPParseError("Invalid header value")

        if key == "content-length":
            if not value.isdigit():
                raise HTTPParseError("Invalid Content-Length")
            
            length = int(value)

            content_lengths.append(length)
        
        elif key == "transfer-encoding":
            transfer_encoding = True 

        if key == "host":
            host_count += 1 

            if not value:
                raise HTTPParseError("Empty Host header")

            if host_count > 1:
                raise HTTPParseError("Duplicate Host header")


        if key in headers:
            headers[key] += ", " + value
        else:
            headers[key] = value

    if http_version == "HTTP/1.1" and host_count != 1:
        raise HTTPParseError(
            "HTTP/1.1 required exactly one Host header"
        )

    if len(content_lengths) > 1:
        raise HTTPParseError(
            "Duplicate Content-Length"
        )
    
    if transfer_encoding:
        raise HTTPParseError("Transfer-Encoding is not supported")

    content_length = content_lengths[0] if content_lengths else 0 

    return (
        method,
        path,
        http_version,
        headers,
        content_length
    )