from pathlib import Path

from content.registry import EPISODES
from lib.validation import validate_episode


ROOT = Path(__file__).parents[1]


def test_all_episodes_have_no_static_errors() -> None:
    for episode in EPISODES.values():
        issues = validate_episode(episode, ROOT)
        assert not [issue for issue in issues if issue.level == "ERROR"]
