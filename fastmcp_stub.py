from __future__ import annotations

from fastapi import FastAPI

class FastMCP:
    """Very small stub of the real FastMCP class used for tests."""

    def __init__(self, name: str, stateless_http: bool | None = None) -> None:
        self.name = name
        self.app = FastAPI(title=name)
        self.tools: list[dict[str, str]] = []

    def tool(self, name: str | None = None, description: str | None = None):
        """Decorator registering a function as a tool and POST endpoint."""
        def decorator(func):
            tool_name = name or func.__name__.replace("_", "-")
            desc = description or (func.__doc__ or "")
            self.tools.append({"name": tool_name, "description": desc})
            self.app.post(f"/{tool_name}")(func)
            return func
        return decorator

    def run(self, **kwargs):
        import uvicorn

        uvicorn.run(self.app, **kwargs)

    # The real FastMCP exposes ``streamable_http_app`` and ``sse_app`` to
    # create ASGI applications for different transports.  Our tests only
    # need a single FastAPI app, so both methods simply return ``self.app``.

    def streamable_http_app(self, mount_path: str | None = None):  # pragma: no cover - stub
        return self.app

    def sse_app(self, mount_path: str | None = None):  # pragma: no cover - stub
        return self.app
