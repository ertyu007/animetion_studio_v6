import pytest

from content.registry import EPISODES, get_episode


def test_registry_has_well_formed_episodes() -> None:
    assert EPISODES, "EPISODES must not be empty"
    for key, episode in EPISODES.items():
        assert key
        assert episode.key == key
        assert episode.title
        assert episode.scene_file
        assert episode.scene_class


def test_get_episode_not_found() -> None:
    with pytest.raises(KeyError):
        get_episode("unknown")

