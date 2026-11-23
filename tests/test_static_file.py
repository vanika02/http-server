import pytest

from static_file import resolve_static_path

def test_resolves_existing_file(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    file_path = static_root / "hello.txt"
    file_path.write_text("hello")

    result = resolve_static_path("/static/hello.txt", static_root)

    assert result == file_path.resolve()