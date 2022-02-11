# -*- coding: utf-8 -*-

"""Version information for :mod:`citation_url`.

Run with ``python -m citation_url.version``
"""

__all__ = [
    "VERSION",
    "get_version",
]

VERSION = "0.0.1"


def get_version(with_git_hash: bool = False):
    """Get the :mod:`citation_url` version string, including a git hash."""
    return VERSION


if __name__ == "__main__":
    print(get_version())  # noqa:T001
