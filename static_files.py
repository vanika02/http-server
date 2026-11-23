from pathlib import Path
from urllib.parse import unquote, urlsplit

STATIC_URL_PREFIX = "/static/"

def resolve_static_path(request_path: str, static_root: Path) -> Path:
    """Resolve a static URL to a file inside the configured document root."""

    url_path = urlsplit(request_path).path 

    if not url_path.startswith(STATIC_URL_PREFIX):
        raise ValueError("Not a static file path")

    encoded_relative_path = url_path[len(STATIC_URL_PREFIX):]
    relative_path = unquote(encoded_relative_path)

    if not relative_path:
        raise ValueError("Static file path is empty")
    
    if "\x00" in relative_path:
        raise ValueError("Null byte in file path")

    if "\\" in relative_path:
        raise PermissionError("Invalid path seperator")
    
    parts = relative_path.split("/")
    
    if any(part in (".", "..") for part in parts):
        raise PermissionError("Path traversal is not allowed")
    
    root = Path(static_root).resolve()
    candidate = (root / relative_path).resolve(strict=True)

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PermissionError("File is outside the static root") from exc 
    
    if not candidate.is_file():
        raise IsADirectoryError("Requested path is not a file")

    return candidate