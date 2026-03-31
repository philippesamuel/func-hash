# func-hash

A micro-library for generating stable, persistent cache keys from function arguments — including callable arguments.

## Origin

This library was extracted from a scraping exercise during a data engineering bootcamp. The task was scraping IMDb; `requests` failed due to a JS challenge, so [Playwright](https://playwright.dev/python/) was used instead.

The scraping function had this signature:

```python
def scrape(url: str, waiting_strategy: Callable[[Page], None]) -> str:
    ...
```

[cachier](https://github.com/python-cachier/cachier) handles persistent caching well, but its default hasher doesn't know what to do with a `Callable` argument — it can't produce a stable key for `waiting_strategy`. `func-hash` solves exactly that.

## What it does

`func_hash` produces a stable `sha256` hex digest from any combination of positional and keyword arguments, including callables.

```python
from cachier import cachier
from func_hash import func_hash

@cachier(hash_func=func_hash)
def scrape(url: str, waiting_strategy: Callable[[Page], None]) -> str:
    ...
```

Two logically identical callables — even if assigned to different variables — produce the same hash:

```python
s1 = lambda page: page.wait_for_load_state("networkidle")
s2 = lambda page: page.wait_for_load_state("networkidle")

func_hash((s1,), {}) == func_hash((s2,), {})  # True
```

Changing the logic invalidates the cache:

```python
s3 = lambda page: page.wait_for_load_state("domcontentloaded")

func_hash((s1,), {}) == func_hash((s3,), {})  # False
```

## How it works

1. Callables are normalized using `ast.unparse(ast.parse(...))` — this strips comments, whitespace, and variable assignment prefixes, leaving only the logic.
2. Collections (`list`, `tuple`, `dict`, `set`, `frozenset`) are recursively normalized with type tags to prevent cross-type collisions.
3. The normalized structure is serialized with `json.dumps(sort_keys=True)` and hashed with `sha256`.

## Requirements

- Python ≥ 3.12
- No runtime dependencies

## Installation

```bash
pip install func-hash
```

## Known limitations

### REPL and Jupyter environments

`func_hash` uses `inspect.getsource()` to extract the source code of callable arguments. This call fails with `OSError` in interactive environments (Python REPL, IPython, Jupyter notebooks) where source is not backed by a file on disk.

When `getsource` fails, `func_hash` falls back to `__qualname__` — which is stable within a session but **not** persistent across sessions or logically equivalent to source-based hashing.

**Concretely:** if you define a lambda in a Jupyter cell, the cache key will be based on the function's qualified name, not its logic. Two cells defining identical lambdas may or may not produce the same key depending on the kernel state.

This is a fundamental limitation of `inspect.getsource` and is out of scope for this library. If you need reliable callable hashing in notebook environments, consider extracting your functions to a `.py` module and importing them — `getsource` works correctly on imported functions.

A source-independent approach (e.g. bytecode normalization across Python versions, or AST extraction from `__code__`) is a valid direction for a fork.

## License

MIT

