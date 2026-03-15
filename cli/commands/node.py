import argparse
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blocks node",
        description="Manage and run nodes.",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    # --- run ---
    p_run = sub.add_parser("run", help="Load and execute a node.")
    p_run.add_argument("-n", "--name", required=True, help="Node name.")
    p_run.add_argument("-d", "--directory", default="myblock/",
                       help="Directory where the node is stored. (default: myblock/)")
    p_run.add_argument("-m", "--method", default=None,
                       help="Method name to execute (default: first registered).")
    p_run.add_argument("-i", "--input", default=None,
                       help="Input data as a JSON object string.")

    # --- info ---
    p_info = sub.add_parser("info", help="Display metadata and registered methods.")
    p_info.add_argument("-n", "--name", required=True, help="Node name.")
    p_info.add_argument("-d", "--directory", default="myblock/",
                        help="Directory where the node is stored. (default: myblock/)")

    # --- list ---
    p_list = sub.add_parser("list", help="List all nodes in a directory.")
    p_list.add_argument("-d", "--directory", default="myblock/",
                        help="Directory to search. (default: myblock/)")

    return parser


def cmd_run(args) -> None:
    from blocks.nodes.node import Node
    from cli.utils import load_json, print_result, kill
    node:Node = None # type: ignore
    result = {}
    data = load_json(args.input)
    try:
        node = Node.load(name=args.name, directory=args.directory, ntype="node")
    except Exception as e:
        kill(f"Could not load node '{args.name}': {e}")
    try:
        result = node.forward(name=args.method, **data)
    except Exception as e:
        kill(f"Execution failed: {e}")
    print("\nResult:")
    print_result(result)


def cmd_info(args) -> None:
    from blocks.nodes.node import Node
    from cli.utils import kill
    node:Node = {} # type: ignore
    try:
        node = Node.load(name=args.name, directory=args.directory, ntype="node")
    except Exception as e:
        kill(f"Could not load node '{args.name}': {e}")
    print(f"Name:      {node.name}")
    print(f"Type:      {node.__ntype__}")
    print(f"Version:   {node.__version__}")
    print(f"ID:        {node.__id__}")
    print(f"Directory: {getattr(node, 'directory', args.directory)}")
    methods = getattr(node, "_register_methods", {})
    if methods:
        print("\nMethods:")
        for method_name, obj in methods.items():
            print(f"  - {method_name}  (type: {obj.ftype})")
    else:
        print("\nMethods: (none registered)")


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
    print(f"Nodes in '{args.directory}':")
    for entry in entries:
        print(f"  - {entry}")


_COMMANDS = {
    "run":  cmd_run,
    "info": cmd_info,
    "list": cmd_list,
}


def run(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)
    _COMMANDS[args.subcommand](args)
