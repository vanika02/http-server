from http_parse import parse

class HTTPRequest:
    """
    A class representing an HTTP request.

    Attributes:
        headers (dict): Dictionary of HTTP headers.
        body (str): Request body.
        method (str): HTTP method (GET, POST, etc.)
        path (str): Requested path
        http_version (str): HTTP version
    """

    def __init__(self, raw_request: str):
        """
        Initialize an HTTPRequest object.

        Args: 
            raw_request (str): Raw HTTP request string.
        """

        self.raw_request = raw_request
        self.headers = {}
        self.body = ""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self._parse()

    def _parse(self):
        """Parse the raw HTTP request into its components."""

        # split the request into headers and body
        parts = self.raw_request.split('\r\n\r\n', 1)
        headers_section = parts[0]
        self.body = parts[1] if len(parts) > 1 else ""

        # split headers into lines
        header_lines = headers_section.split('\r\n')

        # parse the request line (first line)
        if header_lines:
            request_line = header_lines[0].split(' ')
            if len(request_line) >= 3:
                self.method = request_line[0]
                self.path = request_line[1]
                self.http_version = request_line[2]

        
        # parse the headers 
        for line in header_lines[1:]:
            if ":" in line:
                key, value = line.split(':', 1)
                self.headers[key.strip()] = value.strip()

    def _repr_(self):
        return f"HTTPRequest(method='{self.method}', path='{self.path}', headers={len(self.headers)} items)"
        













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