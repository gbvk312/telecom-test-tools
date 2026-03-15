import importlib
from typing import Any, Callable, Dict



class ToolRegistry:
    """Registry for discovering and loading analysis tools."""

    _tools: Dict[str, Callable[..., Any]] = {}

    @classmethod
    def register(cls, name: str, func: Callable[..., Any]):
        """Register a tool function by name."""
        cls._tools[name] = func

    @classmethod
    def get_tool(cls, name: str) -> Callable[..., Any]:
        """Fetch a registered tool function."""
        if name not in cls._tools:
            # Attempt to lazy load from standard paths
            try:
                module = importlib.import_module(f"tools.{name}.api")
                if hasattr(module, "analyze"):
                    cls._tools[name] = module.analyze
                elif hasattr(module, "scan"):
                    cls._tools[name] = module.scan
                else:
                    raise ImportError(
                        f"Tool {name} has no valid entry point (scan/analyze)"
                    )
            except Exception as e:
                raise ImportError(f"Could not load tool {name}: {e}")

        return cls._tools[name]

    @classmethod
    def available_tools(cls) -> list:
        return list(cls._tools.keys())
