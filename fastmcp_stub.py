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
