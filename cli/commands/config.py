import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blocks config",
        description="Manage the global session configuration.",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    # --- show (default when no subcommand) ---
    sub.add_parser("show", help="Show the current session configuration.")

    # --- set ---
    p_set = sub.add_parser("set", help="Set session configuration values.")
    p_set.add_argument("-a", "--author",    default=None, help="Author name.")
    p_set.add_argument("-d", "--directory", default=None, help="Default blocks directory.")
    p_set.add_argument("-e", "--email",     default=None, help="Author email.")
    p_set.add_argument(
        "extra", nargs="*", metavar="key=value",
        help="Additional arbitrary key=value pairs.",
    )

    return parser


def cmd_show(_args=None) -> None:
    from cli.session import load
    cfg = load()
    print("Session configuration:")
    for k, v in cfg.items():
        print(f"  {k}: {v!r}")


def cmd_set(args) -> None:
    from cli.session import set_values
    updates = {}
    if args.author    is not None: updates["author"]    = args.author
    if args.directory is not None: updates["directory"] = args.directory
    if args.email     is not None: updates["email"]     = args.email

    for item in args.extra:
        if "=" not in item:
            print(f"[error] '{item}' must be in key=value form.", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        updates[k.strip()] = v.strip()

    cfg = set_values(**updates)
    print("Configuration updated:")
    for k, v in cfg.items():
        print(f"  {k}: {v!r}")


_COMMANDS = {
    "show": cmd_show,
    "set":  cmd_set,
}


def run(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand is None:
        cmd_show()
        return
    _COMMANDS[args.subcommand](args)
