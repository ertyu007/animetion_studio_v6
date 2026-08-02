import pytest

from content.registry import EPISODES, get_episode


def test_registry_empty() -> None:
    assert set(EPISODES) == set()


def test_get_episode_not_found() -> None:
    with pytest.raises(KeyError):
        get_episode("unknown")

