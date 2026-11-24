from datetime import datetime, timezone

class HTTPResponse:

    STATUS_CODES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        408: "Request Timeout",
        409: "Conflict",
        413: "Content Too Large",
        431: "Request Header Fields Too Large",
        500: "Internal Server Error"
    }

    def __init__(self, status_code=200, headers=None, body="", http_version="HTTP/1.1"):

        if not isinstance(status_code, int) or not 100 <= status_code <= 599:
            raise ValueError("Invalid HTTP status code")

        self.http_version = http_version
        self.status_code = status_code
        self.reason = self.STATUS_CODES.get(status_code, "Unknown Status")

        self.headers = headers.copy() if headers else {}
        self.body = body

    
    def build(self, head_only=False):
        """Serialize the response into HTTP response bytes."""

        if isinstance(self.body, bytes):
            body_bytes = self.body
        elif isinstance(self.body, str):
            body_bytes = self.body.encode("utf-8")
        else:
            raise TypeError("Response body must be str or bytes")

        headers = self.headers.copy()

        if self.status_code == 204:
            body_bytes = b""
            headers = {
                key: value
                for key, value in headers.items()
                if key.lower() != "content-length"
            }
        else:
            if not any(key.lower() == "content-length" for key in headers):
                headers["Content-Length"] = str(len(body_bytes))

            if not any(key.lower() == "content-type" for key in headers):
                headers["Content-Type"] = "text/plain; charset=utf-8"

        if not any(key.lower() == "connection" for key in headers):
            headers["Connection"] = "close"

        if not any(key.lower() == "server" for key in headers):
            headers["Server"] = "VanikaHTTP/1.1"

        if not any(key.lower() == "date" for key in headers):
            headers["Date"] = datetime.now(
                timezone.utc
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")

        response = [
            f"{self.http_version} {self.status_code} {self.reason}"
        ]

        for key, value in headers.items():
            response.append(f"{key}: {value}")

        response.append("")

        header_bytes = "\r\n".join(response).encode("utf-8")

        response_body = b"" if head_only else body_bytes

        return header_bytes + b"\r\n" + response_body
