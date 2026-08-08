"""Episode registry used by CLI and validation."""

from content.cpp_hello_world import SCRIPT as cpp_hello_world
from content.pointer_deref import SCRIPT as pointer_deref

EPISODES = {
    episode.key: episode
    for episode in (
        cpp_hello_world,
        pointer_deref,
    )
}


def get_episode(key: str):
    try:
        return EPISODES[key]
    except KeyError as exc:
        raise KeyError(f"unknown episode {key!r}; choose from {', '.join(sorted(EPISODES))}") from exc