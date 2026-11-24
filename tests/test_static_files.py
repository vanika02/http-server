import pytest

from static_files import resolve_static_path, load_static_file

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

def test_rejects_null_byte(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    with pytest.raises(ValueError):
        resolve_static_path("/static/file%00.txt", static_root)

def test_rejects_backlash(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    with pytest.raises(PermissionError):
        resolve_static_path("/static/folder%5Csecret.txt", static_root)

def test_rejects_missing_file(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    with pytest.raises(FileNotFoundError):
        resolve_static_path("/static/missing.txt", static_root)

def test_rejects_directory(tmp_path):
    static_root = tmp_path / "static"
    directory = static_root / "folder"
    directory.mkdir(parents=True)

    with pytest.raises(IsADirectoryError):
        resolve_static_path("/static/folder", static_root)

def test_rejects_symlink_outside_static_root(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret")

    link = static_root / "secret-link.txt"
    link.symlink_to(outside_file)

    with pytest.raises(PermissionError):
        resolve_static_path("/static/secret-link.txt", static_root)

def test_rejects_non_static_url(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    with pytest.raises(ValueError):
        resolve_static_path("/about", static_root)

def test_loads_text_file(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    file_path = static_root / "hello.txt"
    file_path.write_text("Hello, static files!")

    content, content_type = load_static_file(
        "/static/hello.txt",
        static_root
    )

    assert content == b"Hello, static files!"
    assert content_type == "text/plain"

def test_loads_binary_file_without_modifying_bytes(tmp_path):
    static_root = tmp_path / "static"
    static_root.mkdir()

    expected = bytes([0, 25, 128, 10, 65])
    (static_root / "image.png").write_bytes(expected)

    content, content_type = load_static_file(
        "/static/image.png"
    )

    assert content == expected
    assert content_type == "image/png"