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

    def __init__(self, raw_request: bytes):
        """
        Initialize an HTTPRequest object.

        Args: 
            raw_request (bytes): Raw HTTP request string.
        """

        self.raw_request = raw_request
        self.headers: dict[str, str] = {}
        self.body: bytes = b""
        self.method = ""
        self.path = ""
        self.http_version = ""

        self._parse_request()

    def _parse_request(self):
        """Parse the raw HTTP request into its components."""

        # split the request into headers and body
        parts = self.raw_request.split(b"\r\n\r\n", 1)
        headers_section = parts[0]
        self.body = parts[1] if len(parts) > 1 else b""

        # split headers into lines
        header_lines = headers_section.split(b"\r\n")
        if not header_lines:
            return 

        # parse the request line (first line)
        request_line = header_lines[0].split()

        if len(request_line) >= 3:
            self.method = request_line[0].decode()
            self.path = request_line[1].decode()
            self.http_version = request_line[2].decode()
        
        else:
            raise ValueError("Malformed HTTP request line")
        
        # parse the headers 
        for line in header_lines[1:]:
            if b":" not in line:
                continue
            key, value = line.split(b":", 1)
            self.headers[
                key.strip().decode().lower()
            ] = value.strip().decode()

    def __repr__(self):
        return (
            f"HTTPRequest("
            f"method={self.method}, "
            f"path={self.path}, "
            f"headers={len(self.headers)})"
        )
        













# raw_request = """
# GET /path HTTP/1.1
# Host: example.com
# User-Agent: curl/8.5.0

# {"data": "example"}
# """

# parsed = parse(raw_request)
# print("Headers: ", parsed.headers)       # Access headers (dictionary format)
# print("Body: ", parsed.body)          # Access Body
# print("Path: ", parsed.path)          # Access requested path (/foo/bar)
# print("Method: ", parsed.method)