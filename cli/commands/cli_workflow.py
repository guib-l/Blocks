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
    p_create.add_argument("-i", "--input", default=None, metavar="FILE",
                          help="Optional Python file to register as the first node.")
    p_create.add_argument("-d", "--directory", default=None,
                          help="Directory to save the workflow (default: session directory).")
    p_create.add_argument("-v", "--version", default="0.0.1",
                          help="Workflow version. (default: 0.0.1)")

    # --- run ---
    p_run = sub.add_parser("run", help="Load and execute workflow(s).")
    p_run.add_argument(
        "names", nargs="+", metavar="name",
        help="Workflow name(s) to run. Use 'a > b' (quoted) to chain as a pipeline.",
    )
    p_run.add_argument("-d", "--directory", default=None,
                       help="Directory where the workflow(s) are stored (default: session directory).")
    p_run.add_argument("-i", "--input", default=None,
                       help="Input data: a JSON object string or a path to a .json file.")
    p_run.add_argument("-f", "--format", default="json",
                       help="Load format: json or pickle. (default: json)")

    # --- info ---
    p_info = sub.add_parser("info", help="Display graph structure and node details.")
    p_info.add_argument("-n", "--name", required=True, help="Workflow name.")
    p_info.add_argument("-d", "--directory", default=None,
                        help="Directory where the workflow is stored (default: session directory).")
    p_info.add_argument("-f", "--format", default="json",
                        help="Load format: json or pickle. (default: json)")

    # --- list ---
    p_list = sub.add_parser("list", help="List workflows in a directory, or nodes inside a workflow.")
    p_list.add_argument("-n", "--name", default=None,
                        help="Workflow name: if given, list its registered nodes.")
    p_list.add_argument("-d", "--directory", default=None,
                        help="Directory to search (default: session directory).")

    # --- add ---
    p_add = sub.add_parser("add", help="Add a node to a workflow.")
    p_add.add_argument("block", metavar="<block>", help="Name of the node to add.")
    p_add.add_argument("-n", "--name", required=True, help="Workflow name.")
    p_add.add_argument("-d", "--directory", default=None,
                       help="Directory (default: session directory).")
    p_add.add_argument("-m", "--method", default=None,
                       help="Method name to bind on the node.")
    p_add.add_argument("-p", "--no-input", action="store_true",
                       help="Node does not receive input from the previous node.")
    p_add.add_argument("-k", "--no-output", action="store_true",
                       help="Node output is not forwarded to the next node.")
    p_add.add_argument("-g", "--sequence", default=None, metavar="JSON",
                       help="Fixed JSON input sequence passed to this node.")

    # --- del ---
    p_del = sub.add_parser("del", help="Remove a node from a workflow.")
    p_del.add_argument("block", metavar="<block>", help="Label of the node to remove.")
    p_del.add_argument("-n", "--name", required=True, help="Workflow name.")
    p_del.add_argument("-d", "--directory", default=None,
                       help="Directory (default: session directory).")

    return parser


def _resolve_dir(args_dir):
    """Return directory from args, falling back to the session default."""
    if args_dir:
        return args_dir
    from cli.session import load
    return load().get("directory", "myblock/")


def _parse_pipeline(names):
    """
    Detect a pipeline when a single quoted string contains '>'.
    Multiple bare names (no '>') are treated as independent runs.
    Returns (list_of_names, is_pipeline).
    """
    if len(names) == 1 and ">" in names[0]:
        parts = [p.strip() for p in names[0].split(">") if p.strip()]
        return parts, True
    return names, False


def cmd_create(args) -> None:
    from blocks.nodes.workflow import Workflow
    from blocks.engine.language import Language
    from cli.utils import kill
    from cli.session import load

    session = load()
    directory = _resolve_dir(args.directory)

    try:
        wf = Workflow.create(
            name=args.name,
            directory=directory,
            version=args.version,
            metadata={
                "source": "cli",
                "author": session.get("author", ""),
                "email": session.get("email", ""),
            },
            language=Language.python3_pip(name=args.name, 
                                          directory=directory,
                                          dependencies=[]),
            register_nodes={},
        )
        wf.install()
    except Exception as e:
        kill(f"Could not create workflow '{args.name}': {e}")

    if args.input:
        if not os.path.isfile(args.input):
            kill(f"Python file not found: '{args.input}'")
        _register_file_as_node(wf, args.input, directory)

    print(f"Workflow '{args.name}' created in '{directory}'.")


def _register_file_as_node(wf, filepath, directory) -> None:
    """Create a node from filepath and import it into the workflow."""
    from blocks.nodes.node import Node
    from blocks.asset.python3.install import InstallerPython
    from blocks.engine.environment import EnvironmentBase
    from blocks.engine.language import Language
    from cli.utils import kill

    node_name = os.path.splitext(os.path.basename(filepath))[0]
    try:
        node = Node(
            name=node_name,
            directory=directory,
            mandatory_attr=False,
            installer=InstallerPython,
            installer_config={"auto": True},
            language=Language.python3_pip(name=node_name, 
                                          directory=directory,
                                          dependencies=[]),
            files=[filepath],
            allowed_name=[],
        )
        node.install()
        wf.import_node(node=node, label=node_name)
        wf.install()
    except Exception as e:
        kill(f"Could not register file '{filepath}' as node: {e}")


def cmd_run(args) -> None:
    from cli.utils import load_json

    directory = _resolve_dir(args.directory)
    data = load_json(args.input)
    names, is_pipeline = _parse_pipeline(args.names)

    if is_pipeline:
        _run_pipeline(names, directory, args.format, data)
    else:
        for name in names:
            _run_single(name, directory, args.format, data)


def _run_single(name, directory, fmt, data) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import print_result, kill

    try:
        wf = Workflow.load(name=name, directory=directory, format=fmt)
    except Exception as e:
        kill(f"Could not load workflow '{name}': {e}")
    try:
        result = wf.execute(**data)
    except Exception as e:
        kill(f"Execution of '{name}' failed: {e}")
    print(f"\n[{name}] Result:")
    print_result(result)


def _run_pipeline(names, directory, fmt, data) -> None:
    """Execute a sequence of workflows as a pipeline."""
    from blocks.nodes.workflow import Workflow
    from cli.utils import print_result, kill

    current_data = dict(data)
    for name in names:
        try:
            wf = Workflow.load(name=name, directory=directory, format=fmt)
        except Exception as e:
            kill(f"Could not load workflow '{name}': {e}")
        try:
            result = wf.execute(**current_data)
        except Exception as e:
            kill(f"Execution of '{name}' failed: {e}")
        print(f"[{name}] -> {result}")
        current_data = result if isinstance(result, dict) else {"result": result}

    print("\nFinal result:")
    print_result(current_data)


def cmd_info(args) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import kill

    directory = _resolve_dir(args.directory)
    try:
        wf = Workflow.load(name=args.name, directory=directory, format=args.format)
    except Exception as e:
        kill(f"Could not load workflow '{args.name}': {e}")
    print(f"Name:      {wf.name}")
    print(f"Version:   {wf.__version__}")
    print(f"ID:        {wf.__id__}")
    print(f"Directory: {getattr(wf, 'directory', directory)}")
    print()
    wf.draw()


def cmd_list(args) -> None:
    from cli.utils import kill

    directory = _resolve_dir(args.directory)

    if args.name:
        from blocks.nodes.workflow import Workflow
        try:
            wf = Workflow.load(name=args.name, directory=directory)
        except Exception as e:
            kill(f"Could not load workflow '{args.name}': {e}")
        nodes = getattr(wf, "_register_nodes", {})
        if nodes:
            print(f"Nodes in workflow '{args.name}':")
            for label, reg in nodes.items():
                node_name = reg["node"].name
                method = reg.get("function_name") or "default"
                print(f"  [{label}] {node_name}  (method: {method})")
        else:
            print(f"Workflow '{args.name}' has no registered nodes.")
        return

    if not os.path.isdir(directory):
        kill(f"Directory '{directory}' does not exist.")
    entries = sorted(
        d for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d))
    )
    if not entries:
        print(f"No entries found in '{directory}'.")
        return
    print(f"Workflows in '{directory}':")
    for entry in entries:
        print(f"  - {entry}")


def cmd_add(args) -> None:
    from blocks.nodes.workflow import Workflow
    from blocks.nodes.node import Node
    from cli.utils import load_json, kill

    directory = _resolve_dir(args.directory)

    try:
        wf = Workflow.load(name=args.name, directory=directory)
    except Exception as e:
        kill(f"Could not load workflow '{args.name}': {e}")

    try:
        node = Node.load(name=args.block, directory=directory, ntype="node")
    except Exception as e:
        kill(f"Could not load node '{args.block}': {e}")

    attributes = {}
    if args.no_input:
        attributes["no_input"] = True
    if args.no_output:
        attributes["no_output"] = True
    if args.sequence:
        attributes["input_sequence"] = load_json(args.sequence)

    try:
        wf.import_node(
            node=node,
            label=args.block,
            method_name=args.method,
            directory=directory,
            **attributes,
        )
        wf.install()
    except Exception as e:
        kill(f"Could not add node '{args.block}' to workflow '{args.name}': {e}")

    print(f"Node '{args.block}' added to workflow '{args.name}'.")


def cmd_del(args) -> None:
    from blocks.nodes.workflow import Workflow
    from cli.utils import kill

    directory = _resolve_dir(args.directory)
    try:
        wf = Workflow.load(name=args.name, directory=directory)
    except Exception as e:
        kill(f"Could not load workflow '{args.name}': {e}")

    if args.block not in getattr(wf, "_register_nodes", {}):
        kill(f"Node '{args.block}' not found in workflow '{args.name}'.")

    del wf._register_nodes[args.block]
    wf._register_interface = [
        (label, iface)
        for label, iface in wf._register_interface
        if label != args.block
    ]

    try:
        links_to_remove = [
            (o, t) for o, t in wf.graphics.links
            if o == args.block or t == args.block
        ]
        for o, t in links_to_remove:
            wf.graphics.del_link(o, t)
        wf.communicate.update_graphics(wf.graphics)
    except Exception:
        pass

    try:
        wf.install()
    except Exception as e:
        kill(f"Could not save workflow after deletion: {e}")

    print(f"Node '{args.block}' removed from workflow '{args.name}'.")


_COMMANDS = {
    "create": cmd_create,
    "run":    cmd_run,
    "info":   cmd_info,
    "list":   cmd_list,
    "add":    cmd_add,
    "del":    cmd_del,
}


def run(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)
    _COMMANDS[args.subcommand](args)
