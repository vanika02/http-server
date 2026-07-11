from http_parse import parse

raw_request = """
GET/path HTTP/1.1
Host: example.com
User-Agent: curl/8.5.0

{"data": "example"}
"""

parsed = parse(raw_request)
print(parsed.headers)       # Access headers (dictionary format)
print(parsed.body)          # Access Body
print(parsed.path)          # Access requested path (/foo/bar)