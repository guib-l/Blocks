import argparse
import sys


USAGE = """usage: blocks <command> [<subcommand>] [options]

Commands:
  config      Manage the global session configuration.
  workflow    Manage and run workflows.
  node        Manage and run nodes.
  version     Print the installed blocks version.

Run 'blocks <command> --help' for details on a command.
"""


def cmd_version() -> None:
    from importlib.metadata import version as _version, PackageNotFoundError
    try:
        v = _version("blocks")
    except PackageNotFoundError:
        v = "unknown"
    print(f"blocks {v}")


def main(argv=None) -> None:
    args = sys.argv[1:] if argv is None else argv

    if not args or args[0] in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)

    command = args[0]

    if command == "version":
        cmd_version()

    elif command == "config":
        from cli.commands.config import run as config_run
        config_run(args[1:])

    elif command == "workflow":
        from cli.commands.cli_workflow import run as workflow_run
        workflow_run(args[1:])

    elif command == "node":
        from cli.commands.cli_node import run as node_run
        node_run(args[1:])

    else:
        print(f"[error] Unknown command '{command}'.\n", file=sys.stderr)
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
