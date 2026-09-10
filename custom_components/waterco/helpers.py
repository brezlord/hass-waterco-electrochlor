"""Helper functions for the Waterco Electrochlor integration."""

from __future__ import annotations

from typing import Any


def find_key(data: Any, target_key: str) -> Any:
    """Recursively search dictionaries and lists for a key.

    Returns the value associated with target_key if found, otherwise None.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]

        for value in data.values():
            found = find_key(value, target_key)
            if found is not None:
                return found

    elif isinstance(data, list):
        for value in data:
            found = find_key(value, target_key)
            if found is not None:
                return found

    return None