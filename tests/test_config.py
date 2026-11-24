import pytest 

from config import ServerConfig

def test_default_config_value():
    config = ServerConfig()

    assert config.socket_timeout == 5.0
    assert config.max_header_size == 16 * 1024
    assert config.max_body_size == 1 * 1024 * 1024
    assert config.header_delimiter == b"\r\n\r\n"


def test_custom_config_value():
    config = ServerConfig(
        socket_timeout=0.1,
        max_header_size=8192,
        max_body_size=512 * 1024
    )

    assert config.socket_timeout == 0.1
    assert config.max_header_size == 8192
    assert config.max_body_size == 512 * 1024

@pytest.mark.parametrize("kwargs", [
    {"socket_timeout": -1},
    {"socket_timeout": 0},
    {"max_header_size": -1},
    {"max_header_size": 0},
    {"max_body_size": -1},
    {"header_delimiter": b""}
])
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        ServerConfig(**kwargs)

def test_configuration_is_immutable():
    config = ServerConfig()

    with pytest.raises(AttributeError):
        config.max_body_size = 100

from pathlib import Path

from config import ServerConfig


def test_static_root_defaults_to_project_static_directory():
    config = ServerConfig()

    expected = Path(__file__).resolve().parents[1] / "static"

    assert config.static_root == expected


def test_static_root_accepts_custom_path(tmp_path):
    config = ServerConfig(static_root=tmp_path)

    assert config.static_root == tmp_path.resolve()


def test_static_root_is_absolute():
    config = ServerConfig()

    assert config.static_root.is_absolute()

def test_max_connections_default():
    config = ServerConfig()

    assert config.max_connections == 50


def test_max_connections_custom_value():
    config = ServerConfig(max_connections=10)

    assert config.max_connections == 10


def test_max_connections_must_be_positive():
    with pytest.raises(ValueError):
        ServerConfig(max_connections=0)


def test_max_connections_cannot_be_negative():
    with pytest.raises(ValueError):
        ServerConfig(max_connections=-1)