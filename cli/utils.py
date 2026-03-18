import json
import sys

from typing import Any, NoReturn


def error(msg: str) -> None:
    """Print an error message to stderr."""
    print(f"[error] {msg}", file=sys.stderr)


def kill(msg: str, code: int = 1) -> NoReturn:
    """Print an error message and exit."""
    error(msg)
    sys.exit(code)


def load_json(raw) -> Any:
    """Parse a JSON string from the CLI. Returns {} on empty/None input."""
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            kill(f"--input must be a JSON object, got {type(data).__name__}.")
        return data
    except json.JSONDecodeError as e:
        kill(f"Invalid JSON: {e}")


def print_result(result) -> None:
    """Pretty-print a workflow/node result to stdout."""
    try:
        print(json.dumps(result, indent=2, default=str))
    except Exception:
        print(str(result))
