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
    """
    Parse and validate an HTTP request line and its headers.
    
    Returns:
        method, path, http_version, headers, content_length, is_chunked
    
    """
    
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
    transfer_encodings = []
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

        if any(
            (byte < 32 and byte != 9) or byte == 127
            for byte in value_bytes
        ):
            raise HTTPParseError("Invalid header value")

        try:
            key = key_bytes.decode("ascii").lower()
            value = value_bytes.strip(b" \t").decode("ascii")
            
        except UnicodeDecodeError as exc:
            raise HTTPParseError(
                "Invlid header encoding"
            ) from exc 

        if key == "content-length":
            if not value.isdigit():
                raise HTTPParseError("Invalid Content-Length")

            content_lengths.append(int(value))
        
        elif key == "transfer-encoding":
            transfer_encodings.extend(
                coding.strip().lower()
                for coding in value.split(",")
            )

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
    
    if content_lengths and transfer_encodings:
        raise HTTPParseError(
            "Content-Length and Transfer-Encoding cannot be together"
        )
    
    if transfer_encodings:
        if transfer_encodings != ["chunked"]:
            raise HTTPParseError("Unsupported Transfer-Encoding")
        
        is_chunked = True 
    else:
        is_chunked = False

    content_length = content_lengths[0] if content_lengths else 0 

    return (
        method,
        path,
        http_version,
        headers,
        content_length,
        is_chunked
    )


class IncompleteChunkError(HTTPParseError):
    """Raised when more bytes are needed to complete chunk parsing."""


CHUNK_SIZE_PATTERN = re.compile(
    rb"^[0-9A-Fa-f]+(?:;[^\r\n]*)?$"
)


def read_chunked_body(
    data: bytes,
    max_body_size: int = 10 * 1024 * 1024,
    max_trailer_size: int = 8192,
):
    """
    Decode a complete chunked HTTP body.

    Returns:
        (decoded_body, bytes_consumed)
    """

    body = bytearray()
    position = 0
    data_length = len(data)

    while True:
        line_end = data.find(b"\r\n", position)

        if line_end == -1:
            raise IncompleteChunkError("Incomplete chunk-size line")

        size_line = data[position:line_end]
        position = line_end + 2

        if not size_line or not CHUNK_SIZE_PATTERN.fullmatch(size_line):
            raise HTTPParseError("Invalid chunk size")

        size_token = size_line.split(b";", 1)[0]

        try:
            chunk_size = int(size_token, 16)
        except ValueError as exc:
            raise HTTPParseError("Invalid chunk size") from exc

        if chunk_size == 0:
            trailer_start = position

            while True:
                trailer_end = data.find(b"\r\n", position)

                if trailer_end == -1:
                    raise IncompleteChunkError("Incomplete trailer section")

                trailer_line = data[position:trailer_end]
                position = trailer_end + 2

                if position - trailer_start > max_trailer_size:
                    raise HTTPParseError("Trailer section too large")

                if not trailer_line:
                    return bytes(body), position

                if trailer_line.startswith((b" ", b"\t")):
                    raise HTTPParseError("Folded trailers are not supported")

                if b":" not in trailer_line:
                    raise HTTPParseError("Malformed trailer")

                name, value = trailer_line.split(b":", 1)

                if not METHOD_TOKEN_PATTERN.fullmatch(name):
                    raise HTTPParseError("Invalid trailer name")

                if any(
                    (byte < 32 and byte != 9) or byte == 127
                    for byte in value
                ):
                    raise HTTPParseError("Invalid trailer value")

                if name.lower() in (
                    b"content-length",
                    b"transfer-encoding",
                    b"host",
                ):
                    raise HTTPParseError("Forbidden trailer field")

        if len(body) + chunk_size > max_body_size:
            raise HTTPParseError("Request body too large")

        chunk_end = position + chunk_size

        if chunk_end > data_length:
            raise IncompleteChunkError("Incomplete chunk data")

        if data_length < chunk_end + 2:
            raise IncompleteChunkError("Incomplete chunk delimiter")

        if data[chunk_end:chunk_end + 2] != b"\r\n":
            raise HTTPParseError("Missing CRLF after chunk data")

        body.extend(data[position:chunk_end])
        position = chunk_end + 2
