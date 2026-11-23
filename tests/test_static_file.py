import pytest

from static_file import resolve_static_path

def test_resolves_existing_file(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    file_path = static_root / "hello.txt"
    file_path.write_text("hello")

    result = resolve_static_path("/static/hello.txt", static_root)

    assert result == file_path.resolve()

def test_ignores_query_parameters(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    file_path = static_root / "hello.txt"
    file_path.write_text("hello")

    result = resolve_static_path(
        "/static/hello.txt?version=1",
        static_root
    )

    assert result == file_path.resolve()

@pytest.mark.parametrize(
    "request_path",
    [
        "/static/../secret.txt",
        "/static/%2e%2e/secret.txt",
        "/static/folder/../../secret.txt",
        "/static/%2E%2E/secret.txt"
    ],
)
def test_rejects_path_traversal(tmp_path, request_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    with pytest.raises(PermissionError):
        resolve_static_path(request_path, static_root)