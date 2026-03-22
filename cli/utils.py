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
    """Parse JSON input from the CLI.

    *raw* can be:
    - ``None`` / empty string  → returns ``{}``
    - a path to an existing ``.json`` file → file is read and parsed
    - a raw JSON object string  → parsed directly
    """
    if not raw:
        return {}
    # Treat as a file path when the value ends with .json or points to an existing file
    import os
    if raw.endswith(".json") or os.path.isfile(raw):
        if not os.path.isfile(raw):
            kill(f"JSON file not found: '{raw}'")
        try:
            with open(raw, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as e:
            kill(f"Invalid JSON in file '{raw}': {e}")
        except OSError as e:
            kill(f"Could not read file '{raw}': {e}")
    else:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            kill(f"Invalid JSON: {e}")
    if not isinstance(data, dict):
        kill(f"--input must be a JSON object, got {type(data).__name__}.")
    return data


def print_result(result) -> None:
    """Pretty-print a workflow/node result to stdout."""
    try:
        print(json.dumps(result, indent=2, default=str))
    except Exception:
        print(str(result))
