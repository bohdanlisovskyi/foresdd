"""Reading-time estimate: whole minutes at a fixed reading speed (ADR-0001)."""

import math

WORDS_PER_MINUTE = 200


def word_count(text):
    """Number of whitespace-separated words in text."""
    return len(text.split())


def minutes(text):
    """Estimated reading time in whole minutes, rounded up; 0 for empty text."""
    return math.ceil(word_count(text) / WORDS_PER_MINUTE)


def label(text):
    """Human label shown next to an article."""
    mins = minutes(text)
    if mins == 0:
        return "under a minute"
    return f"{mins} min read"
