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