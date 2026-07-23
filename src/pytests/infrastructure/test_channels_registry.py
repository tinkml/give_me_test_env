import pytest
import structlog

from src.infrastructure.channels import ChannelConfig, ChannelsRegistry, WebhookTokens, load_channel_configs


def _write_yaml(tmp_path, content: str) -> str:
    path = tmp_path / "channels.yml"
    path.write_text(content)
    return str(path)


def test_load_channel_configs_parses_yaml_into_channel_configs(tmp_path) -> None:
    path = _write_yaml(
        tmp_path,
        """
        channels:
          akb:
            token_env: WEBHOOK_TOKEN_AKB
            stands:
              - akb1
              - slplay4
          sl:
            token_env: WEBHOOK_TOKEN_SL
            stands:
              - dev-1
        """,
    )

    configs = load_channel_configs(path)

    assert configs == [
        ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1", "slplay4"]),
        ChannelConfig(team="sl", token_env="WEBHOOK_TOKEN_SL", stands=["dev-1"]),
    ]


def test_webhook_tokens_from_env_reads_only_requested_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBHOOK_TOKEN_AKB", "akb-secret")
    monkeypatch.setenv("WEBHOOK_TOKEN_UNRELATED", "should-not-appear")

    tokens = WebhookTokens.from_env(["WEBHOOK_TOKEN_AKB"])

    assert tokens == {"WEBHOOK_TOKEN_AKB": "akb-secret"}


def test_webhook_tokens_from_env_skips_missing_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEBHOOK_TOKEN_MISSING", raising=False)

    tokens = WebhookTokens.from_env(["WEBHOOK_TOKEN_MISSING"])

    assert tokens == {}


def test_channels_registry_maps_token_to_team_and_team_to_stands() -> None:
    configs = [
        ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1", "slplay4"]),
        ChannelConfig(team="sl", token_env="WEBHOOK_TOKEN_SL", stands=["dev-1"]),
    ]
    tokens = {"WEBHOOK_TOKEN_AKB": "akb-secret", "WEBHOOK_TOKEN_SL": "sl-secret"}

    registry = ChannelsRegistry.build(configs, tokens)

    assert registry.team_for_token("akb-secret") == "akb"
    assert registry.team_for_token("sl-secret") == "sl"
    assert registry.stands_for_team("akb") == ["akb1", "slplay4"]
    assert registry.stands_for_team("sl") == ["dev-1"]


def test_channels_registry_returns_none_for_unknown_token() -> None:
    registry = ChannelsRegistry.build([], {})

    assert registry.team_for_token("unknown") is None


def test_channels_registry_skips_team_with_missing_token_and_logs_warning() -> None:
    configs = [ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"])]

    with structlog.testing.capture_logs() as logs:
        registry = ChannelsRegistry.build(configs, {})

    assert registry.team_for_token("anything") is None
    assert registry.stands_for_team("akb") == []
    assert registry.teams() == []

    events = [entry["event"] for entry in logs]
    assert "channel_token_missing" in events


def test_channels_registry_from_config_builds_from_yaml_and_env(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _write_yaml(
        tmp_path,
        """
        channels:
          akb:
            token_env: WEBHOOK_TOKEN_AKB
            stands:
              - akb1
        """,
    )
    monkeypatch.setenv("WEBHOOK_TOKEN_AKB", "akb-secret")

    registry = ChannelsRegistry.from_config(path)

    assert registry.team_for_token("akb-secret") == "akb"
    assert registry.stands_for_team("akb") == ["akb1"]
