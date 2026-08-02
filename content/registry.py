"""Episode registry used by CLI and validation."""

EPISODES = {}


def get_episode(key: str):
    try:
        return EPISODES[key]
    except KeyError as exc:
        raise KeyError(f"unknown episode {key!r}; choose from {', '.join(sorted(EPISODES))}") from exc
