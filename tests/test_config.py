from pydantic import SecretStr

from saarige.config import Settings


def test_settings_read_from_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    s = Settings(_env_file=None)
    assert s.llm_api_key.get_secret_value() == "test-key"
    assert s.log_level == "INFO"


def test_api_key_hidden_when_printed(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "super-secret")
    s = Settings(_env_file=None)
    assert "super-secret" not in repr(s)
    assert isinstance(s.llm_api_key, SecretStr)
