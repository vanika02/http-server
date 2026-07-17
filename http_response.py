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

    def __init__(self, status_code=200, headers=None, body=""):

        self.status_code = status_code
        self.reason = self.STATUS_CODES[status_code]

        self.headers = headers or {}

        self.body = body

    def build(self):

        lines = []

        lines.append(
            f"HTTP/1.1 {self.status_code} {self.reason}"
        )

        for key, value in self.headers.items():
            lines.append(
                f"{key}: {value}"
            )
        
        lines.append("")

        lines.append(self.body)

        return "\r\n".join(lines).encode()


# current questions are why headers are {}
# init function explanation, self  and this line self.reason = self.STATUS_CODES[status_code]