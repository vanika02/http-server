class HTTPResponse:

    STATUS_CODES = {
        200: "OK",
        404: "Not Found",
        500: "Internal Server Error"
    }

    def __init__(self, status_code=200, headers=None, body=""):

        self.status_code = status_code
        self.reason = self.STATUS_CODES[status_code]

        self.headers = headers or {}

        self.body = body