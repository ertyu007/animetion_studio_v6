"""Text helpers shared by narration, captions, and validation."""

from __future__ import annotations

import re
from typing import Tuple


_SPACE = re.compile(r"\s+")
_MARKUP = re.compile(r"\[\[([^\[\]]+?)\]\]")


def normalize_space(text: str) -> str:
    return _SPACE.sub(" ", text.strip())


def markup_is_balanced(text: str) -> bool:
    index = 0
    while index < len(text):
        opening = text.find("[[", index)
        closing = text.find("]]", index)
        if opening < 0 and closing < 0:
            return True
        if opening < 0 or closing < opening:
            return False
        closing = text.find("]]", opening + 2)
        if closing < 0:
            return False
        body = text[opening + 2 : closing]
        if not body.strip() or "[[" in body:
            return False
        index = closing + 2
    return True


def parse_highlights(text: str) -> Tuple[str, Tuple[str, ...]]:
    if not markup_is_balanced(text):
        raise ValueError(f"invalid highlight markup: {text!r}")
    highlights = tuple(normalize_space(match.group(1)) for match in _MARKUP.finditer(text))
    clean = _MARKUP.sub(lambda match: match.group(1), text)
    return normalize_space(clean), highlights


def wrap_text(text: str, max_chars: int = 34, max_lines: int = 2) -> str:
    if max_chars < 4 or max_lines < 1:
        raise ValueError("invalid wrap limits")
    clean = normalize_space(text)
    if not clean:
        return ""
    words = clean.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        chunks = [word[i : i + max_chars] for i in range(0, len(word), max_chars)] or [word]
        for chunk in chunks:
            candidate = chunk if not current else f"{current} {chunk}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = chunk
    if current:
        lines.append(current)
    if len(lines) <= max_lines:
        return "\n".join(lines)
    result = lines[:max_lines]
    overflow = " ".join(lines[max_lines - 1 :])
    result[-1] = overflow[: max_chars - 1].rstrip() + "…"
    return "\n".join(result)
