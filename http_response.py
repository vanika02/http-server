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
        405: "Method not allowed",
        500: "Internal Server Error"
    }

    def __init__(self, status_code=200, headers=None, body="", http_version="HTTP/1.1"):

        self.http_version = http_version
        self.status_code = status_code
        self.reason = self.STATUS_CODES.get(status_code, "Unknown Status")

        self.headers = headers.copy() if headers else {}

        self.body = body

    def build(self):
        
        body_bytes = self.body.encode("utf-8")

        self.headers.setdefault(
            "Content-Length",
            str(len(body_bytes))
        )

        self.headers.setdefault(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.headers.setdefault(
            "Connection",
            "close"
        )

        self.headers.setdefault(
            "Server",
            "VanikaHTTP/1.1"
        )

        self.headers.setdefault(
            "Date",
            datetime.now(timezone.utc).strftime(
                "%a, %d, %b, %Y %H:%M:%S GMT"
            )
        )

        response = []

        response.append(
            f"{self.http_version} {self.status_code} {self.reason}"
        )

        for key, value in self.headers.items():
            response.append(
                f"{key}: {value}"
            )
        
        response.append("")

        header_bytes = "\r\n".join(response).encode("utf-8")

        return header_bytes + b"\r\n" + body_bytes


# current questions are why headers are {}
# init function explanation, self  and this line self.reason = self.STATUS_CODES[status_code]