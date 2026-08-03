"""Episode registry used by CLI and validation."""

from content.oop_robot_factory import SCRIPT as oop_robot_factory

EPISODES = {
    episode.key: episode
    for episode in (
        oop_robot_factory,
    )
}


def get_episode(key: str):
    try:
        return EPISODES[key]
    except KeyError as exc:
        raise KeyError(f"unknown episode {key!r}; choose from {', '.join(sorted(EPISODES))}") from exc