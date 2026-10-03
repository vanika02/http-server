from server import _read_until_content_length

class FakeSocket:

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def recv(self, size):
        return next(self.chunks)

        