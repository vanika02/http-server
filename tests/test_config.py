from config import ServerConfig

def test_default_config_value():
    config = ServerConfig()

    assert config.socket_timeout == 5.0
    assert config.max_header_size == 16 * 1024
    assert config.max_body_size == 1 * 1024 * 1024
    assert config.header_delimiter == b"\r\n\r\n"