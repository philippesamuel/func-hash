import ast
import functools
import hashlib
import inspect
import json
import textwrap
from typing import Any


def _normalize(arg: Any) -> Any:
    """Recursively converts an argument into a JSON-serializable structure."""
    # Unwrap partial before any other callable handling
    if isinstance(arg, functools.partial):
        return {
            "__partial__": {
                "func": _normalize(arg.func),
                "args": [_normalize(a) for a in arg.args],
                "kwargs": {k: _normalize(v) for k, v in sorted(arg.keywords.items())},
            }
        }

    if callable(arg):
        try:
            source = inspect.getsource(arg)
            tree = ast.parse(textwrap.dedent(source))
            for node in ast.walk(tree):
                if isinstance(node, ast.Lambda):
                    return {"__callable__": ast.unparse(node)}
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    return {
                        "__callable__": {
                            "args": ast.unparse(node.args),
                            "body": [ast.unparse(stmt) for stmt in node.body],
                        }
                    }
        except (OSError, TypeError):
            pass
        # Built-ins and C extensions: qualname is the best persistent identifier
        return {"__callable__": getattr(arg, "__qualname__", repr(arg))}

    if isinstance(arg, dict):
        return {"__dict__": [[k, _normalize(v)] for k, v in sorted(arg.items())]}

    if isinstance(arg, (list, tuple)):
        return {"__" + type(arg).__name__ + "__": [_normalize(i) for i in arg]}

    if isinstance(arg, (set, frozenset)):
        return {"__" + type(arg).__name__ + "__": sorted(_normalize(i) for i in arg)}

    # Primitives: int, float, str, bool, None — JSON-safe as-is
    if isinstance(arg, int | float | str | bool | type(None)):
        return arg

    # Fallback: repr with type tag to avoid cross-type collisions
    return {"__unknown__": type(arg).__qualname__, "repr": repr(arg)}


def func_hash(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Generates a stable sha256 hex digest for persistent caching with cachier.

    Usage with cachier:
        @cachier(hash_func=func_hash)
        def my_func(...): ...

    Args:
        args:   Positional arguments passed to the cached function.
        kwargs: Keyword arguments passed to the cached function.

    Returns:
        A hex digest string suitable as a persistent cache key.
    """
    normalized = {
        "args": [_normalize(a) for a in args],
        "kwargs": {k: _normalize(v) for k, v in sorted(kwargs.items())},
    }
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()
