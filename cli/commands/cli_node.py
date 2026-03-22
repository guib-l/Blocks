import argparse
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blocks node",
        description="Manage and run nodes.",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    # --- create ---
    p_create = sub.add_parser("create", help="Create a node from a Python file.")
    p_create.add_argument("-n", "--name", required=True, help="Node name.")
    p_create.add_argument("-i", "--input", required=True, metavar="FILE",
                          help="Python file containing the node function(s).")
    p_create.add_argument("-d", "--directory", default=None,
                          help="Directory to save the node (default: session directory).")
    p_create.add_argument("-v", "--version", default="0.0.1",
                          help="Node version. (default: 0.0.1)")

    # --- run ---
    p_run = sub.add_parser("run", help="Load and execute node(s).")
    p_run.add_argument(
        "names", nargs="+", metavar="name",
        help="Node name(s) to run. Use 'a > b' (quoted) to chain as a pipeline.",
    )
    p_run.add_argument("-d", "--directory", default=None,
                       help="Directory where the node(s) are stored (default: session directory).")
    p_run.add_argument("-m", "--method", default=None,
                       help="Method name to execute (default: first registered).")
    p_run.add_argument("-i", "--input", default=None,
                       help="Input data: a JSON object string or a path to a .json file.")

    # --- info ---
    p_info = sub.add_parser("info", help="Display metadata and registered methods.")
    p_info.add_argument("-n", "--name", required=True, help="Node name.")
    p_info.add_argument("-d", "--directory", default=None,
                        help="Directory where the node is stored (default: session directory).")

    # --- list ---
    p_list = sub.add_parser("list", help="List nodes in a directory, or methods inside a node.")
    p_list.add_argument("-n", "--name", default=None,
                        help="Node name: if given, list its methods instead.")
    p_list.add_argument("-d", "--directory", default=None,
                        help="Directory to search (default: session directory).")

    return parser


def _resolve_dir(args_dir):
    """Return directory from args, falling back to the session default."""
    if args_dir:
        return args_dir
    from cli.session import load
    return load().get("directory", "myblock/")


def _parse_pipeline(names):
    """
    Parse the names list into pipeline stages.
    A pipeline is detected when a single quoted string contains '>'.
    Multiple names without '>' are treated as independent runs.
    Returns (list_of_names, is_pipeline).
    """
    if len(names) == 1 and ">" in names[0]:
        parts = [p.strip() for p in names[0].split(">") if p.strip()]
        return parts, True
    return names, False


def cmd_create(args) -> None:
    from blocks.nodes.node import Node
    from blocks.asset.python3.install import InstallerPython
    from blocks.engine.environment import EnvironmentBase
    from blocks.engine.execute import Execute
    from blocks.engine.language import Language
    from cli.utils import kill
    from cli.session import load

    session = load()
    directory = _resolve_dir(args.directory)

    if not os.path.isfile(args.input):
        kill(f"Python file not found: '{args.input}'")

    try:
        node = Node(
            name=args.name,
            version=args.version,
            directory=directory,
            mandatory_attr=False,
            language=Language.python3_pip(name=args.name, 
                                          directory=directory,
                                          dependencies=[]),
            metadata={
                "source": "cli",
                "author": session.get("author", ""),
                "email": session.get("email", ""),
            },
            installer=InstallerPython,
            installer_config={"auto": True},
            files=[args.input],
            allowed_name=[],
        )
        node.install()
    except Exception as e:
        kill(f"Could not create node '{args.name}': {e}")

    print(f"Node '{args.name}' created in '{directory}'.")


def cmd_run(args) -> None:
    from cli.utils import load_json

    directory = _resolve_dir(args.directory)
    data = load_json(args.input)
    names, is_pipeline = _parse_pipeline(args.names)

    if is_pipeline:
        _run_pipeline(names, directory, data, args.method)
    else:
        for name in names:
            _run_single(name, directory, data, args.method)


def _run_single(name, directory, data, method) -> None:
    from blocks.nodes.node import Node
    from cli.utils import print_result, kill

    node = None
    try:
        node = Node.load(name=name, directory=directory, ntype="node")
    except Exception as e:
        kill(f"Could not load node '{name}': {e}")
    try:
        result = node.forward(name=method, **data)
    except Exception as e:
        kill(f"Execution of '{name}' failed: {e}")
    print(f"\n[{name}] Result:")
    print_result(result)


def _run_pipeline(names, directory, data, method) -> None:
    """
    Execute nodes as a pipeline: the output of each node
    becomes the input of the next.
    """
    from blocks.nodes.node import Node
    from cli.utils import print_result, kill

    current_data = dict(data)
    for name in names:
        node = None
        try:
            node = Node.load(name=name, directory=directory, ntype="node")
        except Exception as e:
            kill(f"Could not load node '{name}': {e}")
        try:
            result = node.forward(name=method, **current_data)
        except Exception as e:
            kill(f"Execution of '{name}' failed: {e}")
        print(f"[{name}] -> {result}")
        current_data = result if isinstance(result, dict) else {"result": result}

    print("\nFinal result:")
    print_result(current_data)


def cmd_info(args) -> None:
    from blocks.nodes.node import Node
    from cli.utils import kill

    directory = _resolve_dir(args.directory)
    node = None
    try:
        node = Node.load(name=args.name, directory=directory, ntype="node")
    except Exception as e:
        kill(f"Could not load node '{args.name}': {e}")
    print(f"Name:      {node.name}")
    print(f"Type:      {node.__ntype__}")
    print(f"Version:   {node.__version__}")
    print(f"ID:        {node.__id__}")
    print(f"Directory: {getattr(node, 'directory', directory)}")
    methods = getattr(node, "_register_methods", {})
    if methods:
        print("\nMethods:")
        for method_name, obj in methods.items():
            print(f"  - {method_name}  (type: {obj.ftype})")
    else:
        print("\nMethods: (none registered)")


def cmd_list(args) -> None:
    from cli.utils import kill

    directory = _resolve_dir(args.directory)

    if args.name:
        # List methods inside the named node
        from blocks.nodes.node import Node
        node = None
        try:
            node = Node.load(name=args.name, directory=directory, ntype="node")
        except Exception as e:
            kill(f"Could not load node '{args.name}': {e}")
        methods = getattr(node, "_register_methods", {})
        if methods:
            print(f"Methods in node '{args.name}':")
            for method_name, obj in methods.items():
                print(f"  - {method_name}  (type: {obj.ftype})")
        else:
            print(f"Node '{args.name}' has no registered methods.")
        return

    # Otherwise list all entries in the directory
    if not os.path.isdir(directory):
        kill(f"Directory '{directory}' does not exist.")
    entries = sorted(
        d for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d))
    )
    if not entries:
        print(f"No entries found in '{directory}'.")
        return
    print(f"Nodes in '{directory}':")
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
