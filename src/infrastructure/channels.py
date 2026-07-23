import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.infrastructure.logger import logger


@dataclass(frozen=True)
class ChannelConfig:
    team: str
    token_env: str
    stands: list[str]


def load_channel_configs(path: str) -> list[ChannelConfig]:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    channels = raw.get("channels", {})
    return [
        ChannelConfig(team=team, token_env=data["token_env"], stands=list(data["stands"]))
        for team, data in channels.items()
    ]


class WebhookTokens:
    @staticmethod
    def from_env(token_env_names: Iterable[str]) -> dict[str, str]:
        return {name: value for name in token_env_names if (value := os.environ.get(name)) is not None}


@dataclass(frozen=True)
class ChannelsRegistry:
    _team_by_token: dict[str, str] = field(default_factory=dict)
    _stands_by_team: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def build(cls, channel_configs: list[ChannelConfig], tokens: dict[str, str]) -> "ChannelsRegistry":
        team_by_token: dict[str, str] = {}
        stands_by_team: dict[str, list[str]] = {}

        for config in channel_configs:
            token = tokens.get(config.token_env)
            if token is None:
                logger.warning("channel_token_missing", team=config.team, token_env=config.token_env)
                continue
            team_by_token[token] = config.team
            stands_by_team[config.team] = config.stands

        return cls(team_by_token, stands_by_team)

    @classmethod
    def from_config(cls, path: str) -> "ChannelsRegistry":
        channel_configs = load_channel_configs(path)
        tokens = WebhookTokens.from_env(config.token_env for config in channel_configs)
        return cls.build(channel_configs, tokens)

    def team_for_token(self, token: str) -> str | None:
        return self._team_by_token.get(token)

    def stands_for_team(self, team: str) -> list[str]:
        return self._stands_by_team.get(team, [])

    def teams(self) -> list[str]:
        return list(self._stands_by_team)
