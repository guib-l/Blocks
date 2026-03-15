import argparse
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blocks workflow",
        description="Manage and run workflows.",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    # --- create ---
    p_create = sub.add_parser("create", help="Create and save a new empty workflow.")
    p_create.add_argument("-n", "--name", required=True, help="Workflow name.")
    p_create.add_argument("-d", "--directory", default="myblock/",
                          help="Directory to save the workflow. (default: myblock/)")
    p_create.add_argument("-v", "--version", default="0.0.1",
                          help="Workflow version. (default: 0.0.1)")

    # --- run ---
    p_run = sub.add_parser("run", help="Load and execute a workflow.")
    p_run.add_argument("-n", "--name", required=True, help="Workflow name to run.")
    p_run.add_argument("-d", "--directory", default="myblock/",
                       help="Directory where the workflow is stored. (default: myblock/)")
    p_run.add_argument("-i", "--input", default=None,
                       help="Input data as a JSON object string.")
    p_run.add_argument("-f", "--format", default="json",
                       help="Load format: json or pickle. (default: json)")

    # --- info ---
    p_info = sub.add_parser("info", help="Display graph structure and node details.")
    p_info.add_argument("-n", "--name", required=True, help="Workflow name.")
    p_info.add_argument("-d", "--directory", default="myblock/",
                        help="Directory where the workflow is stored. (default: myblock/)")
    p_info.add_argument("-f", "--format", default="json",
                        help="Load format: json or pickle. (default: json)")

    # --- list ---
    p_list = sub.add_parser("list", help="List all workflows in a directory.")
    p_list.add_argument("-d", "--directory", default="myblock/",
                        help="Directory to search. (default: myblock/)")

    return parser


def cmd_create(args) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import kill
    try:
        wf = Workflow.create(name=args.name, directory=args.directory, version=args.version)
        wf.install()
    except Exception as e:
        kill(f"Could not create workflow '{args.name}': {e}")
    print(f"Workflow '{args.name}' created in '{args.directory}'.")


def cmd_run(args) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import load_json, print_result, kill
    data = load_json(args.input)
    result = {}
    wf:Workflow = None # type: ignore
    try:
        wf = Workflow.load(name=args.name, directory=args.directory, format=args.format)
    except Exception as e:
        kill(f"Could not load workflow '{args.name}': {e}")
    try:
        result = wf.execute(**data)
    except Exception as e:
        kill(f"Execution failed: {e}")
    print("\nResult:")
    print_result(result)


def cmd_info(args) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import kill
    wf:Workflow = None # type: ignore
    try:
        wf = Workflow.load(name=args.name, directory=args.directory, format=args.format)
    except Exception as e:
        kill(f"Could not load workflow '{args.name}': {e}")
    print(f"Name:      {wf.name}")
    print(f"Version:   {wf.__version__}")
    print(f"ID:        {wf.__id__}")
    print(f"Directory: {getattr(wf, 'directory', args.directory)}")
    print()
    wf.draw()


def cmd_list(args) -> None:
    from cli.utils import kill
    if not os.path.isdir(args.directory):
        kill(f"Directory '{args.directory}' does not exist.")
    entries = sorted(
        d for d in os.listdir(args.directory)
        if os.path.isdir(os.path.join(args.directory, d))
    )
    if not entries:
        print(f"No entries found in '{args.directory}'.")
        return
    print(f"Workflows in '{args.directory}':")
    for entry in entries:
        print(f"  - {entry}")


_COMMANDS = {
    "create": cmd_create,
    "run":    cmd_run,
    "info":   cmd_info,
    "list":   cmd_list,
}


def run(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)
    _COMMANDS[args.subcommand](args)
