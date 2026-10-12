class HTTPParseError(Exception):
    """Raised when an HTTP request cannot be parsed or framed."""

class HTTPRequestTooLarge(Exception):
    """Raised when an HTTP request exceeds configured size limits."""