"""Episode registry used by CLI and validation."""

from content.cpp_hello_world import SCRIPT as cpp_hello_world

EPISODES = {
    episode.key: episode
    for episode in (
        cpp_hello_world,
    )
}


def get_episode(key: str):
    try:
        return EPISODES[key]
    except KeyError as exc:
        raise KeyError(f"unknown episode {key!r}; choose from {', '.join(sorted(EPISODES))}") from exc