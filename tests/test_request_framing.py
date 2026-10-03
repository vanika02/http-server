from server import _read_until_content_length

class FakeSocket:

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def recv(self, size):
        return next(self.chunks)

def test_reads_complete_request():

    request = (
        b"POST /signup HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Length: 13\r\n"
        b"\r\n"
        b'{"name":"bob"}'
    )

    sock = FakeSocket([request])
    buffer = bytearray()

    raw_request = _read_until_content_length(
        sock,
        buffer
    )

    assert raw_request == request
    assert buffer == bytearray()