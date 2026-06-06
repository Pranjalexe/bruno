from bruno.mcp_servers.env_server import get_env, list_env
from bruno.mcp_servers.filesystem_server import is_allowed


def test_filesystem_is_allowed(monkeypatch, tmp_path):
    monkeypatch.setenv("BRUNO_ALLOWED_DIRS", str(tmp_path))

    # Inside allowed
    inside = tmp_path / "test.txt"
    assert is_allowed(inside)

    # Outside allowed
    outside = tmp_path.parent / "test.txt"
    assert not is_allowed(outside)

def test_env_redaction(monkeypatch):
    monkeypatch.setenv("TEST_KEY", "secret-value")
    monkeypatch.setenv("NORMAL_VAR", "public-value")

    assert get_env("TEST_KEY") == "***REDACTED***"
    assert get_env("NORMAL_VAR") == "public-value"

    all_env = list_env()
    assert all_env["TEST_KEY"] == "***REDACTED***"
    assert all_env["NORMAL_VAR"] == "public-value"
