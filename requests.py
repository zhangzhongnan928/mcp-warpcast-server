"""Minimal stub of the ``requests`` module used during testing.

This file provides a small subset of the real ``requests`` API so that the
application code can be imported without pulling in the actual dependency or
performing network calls.  Each HTTP method simply raises ``NotImplementedError``
so tests can monkeypatch the functions as needed.
"""


class RequestException(Exception):
    """Exception mimicking ``requests.RequestException``."""


class Response:
    """Simple container for JSON data returned by mocked requests."""

    def __init__(self, json_data=None, status_code: int = 200) -> None:
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RequestException(f"Status {self.status_code}")


def post(*args, **kwargs):
    """Placeholder for ``requests.post``."""

    raise NotImplementedError("requests.post is not implemented in the stub")


def get(*args, **kwargs):
    """Placeholder for ``requests.get``."""

    raise NotImplementedError("requests.get is not implemented in the stub")


class exceptions:
    """Namespace for exception classes to mirror ``requests.exceptions``."""

    RequestException = RequestException

