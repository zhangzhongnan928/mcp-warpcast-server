"""Minimal stub of the ``httpx`` module used for testing.

This provides the ``AsyncClient`` class and ``HTTPError`` exception so that
modules importing ``httpx`` can be loaded without the real dependency.
All HTTP methods simply raise ``NotImplementedError``.
"""

class HTTPError(Exception):
    """Base HTTPX error class."""


class AsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, *args, **kwargs):
        raise NotImplementedError("AsyncClient.get is not implemented in the stub")

    async def post(self, *args, **kwargs):
        raise NotImplementedError("AsyncClient.post is not implemented in the stub")
