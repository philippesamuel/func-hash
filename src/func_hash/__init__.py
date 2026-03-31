import inspect
import re
from typing import Any, Dict, Tuple


def _hash_arg(arg: Any) -> Any:
    """Recursively converts an argument into a hashable primitive."""
    if callable(arg):
        try:
            source = inspect.getsource(arg).strip()

            # Use regex to find the start of the logic (lambda or def)
            # This removes variable assignments like 'l1 = '
            match = re.search(r"((lambda|def)\s.*)", source)
            if match:
                return match.group(1)
            return source
        except (OSError, TypeError):
            if hasattr(arg, "__code__"):
                # Bytecode is a stable bytes object
                return arg.__code__.co_code
            return str(arg)

    # Handle basic collections to ensure they are also hashable
    if isinstance(arg, list):
        return tuple(_hash_arg(i) for i in arg)
    if isinstance(arg, dict):
        return tuple((k, _hash_arg(v)) for k, v in sorted(arg.items()))

    return arg


def func_hash(args: Tuple[Any, ...], kwds: Dict[str, Any]) -> Tuple[Any, ...]:
    """Generates a stable, nested tuple for persistent caching.

    Args:
        args: Positional arguments.
        kwds: Keyword arguments.

    Returns:
        A tuple containing hashable representations of all logic and data.
    """
    pos_part = tuple(_hash_arg(a) for a in args)
    # Sorting keywords is essential for cache stability
    kw_part = tuple((k, _hash_arg(v)) for k, v in sorted(kwds.items()))

    return pos_part + kw_part
