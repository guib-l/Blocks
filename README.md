# Blocks

Code manager written in Python, available for all languages.

## Installation

```bash
pip install -e .
```

Requires Python ≥ 3.8. No external CLI dependency — the CLI relies solely on the standard library.

---

## CLI

After installation, the `blocks` command is available:

```bash
blocks --help
```

---

### Session configuration

The session stores your defaults (author, directory, email) in `~/.blocks/session.json`.
All commands that accept `-d` fall back to the session directory when the option is omitted.

```bash
# Show current session configuration
blocks config
blocks config show

# Set session values
blocks config set -a "Jane Doe" -e "jane@example.com" -d myblock/

# Set arbitrary extra keys
blocks config set project=my_project
```

| Option | Description |
|---|---|
| `-a` / `--author` | Author name |
| `-d` / `--directory` | Default blocks directory |
| `-e` / `--email` | Author email |
| `key=value` | Any additional key |

---

### Nodes

| Command | Description |
|---|---|
| `blocks node create` | Create a node from a Python file |
| `blocks node run` | Execute one or more nodes |
| `blocks node info` | Display metadata and registered methods |
| `blocks node list` | List nodes in a directory, or methods inside a node |

```bash
# Create a node from a Python file (python3_pip by default)
blocks node create -n my_node -i path/to/functions.py
blocks node create -n my_node -i path/to/functions.py -d myblock/ -v 1.0.0

# Run a single node
blocks node run my_node -i '{"n": 10}'

# Run multiple nodes independently (no data passing between them)
blocks node run node_a node_b -i '{"n": 10}'

# Run a pipeline: output of node_a feeds into node_b (quote the string)
blocks node run "node_a > node_b > node_c" -i '{"n": 10}'

# Specify a method explicitly
blocks node run my_node -m my_function -i '{"n": 10}'

# Inspect a node
blocks node info -n my_node

# List all nodes in a directory
blocks node list

# List methods registered in a specific node
blocks node list -n my_node
```

---

### Workflows

| Command | Description |
|---|---|
| `blocks workflow create` | Create and save a new empty workflow |
| `blocks workflow run` | Execute one or more workflows |
| `blocks workflow info` | Display graph structure and node details |
| `blocks workflow list` | List workflows, or nodes inside a workflow |
| `blocks workflow add` | Add a node to a workflow |
| `blocks workflow del` | Remove a node from a workflow |

```bash
# Create an empty workflow
blocks workflow create -n my_workflow

# Create a workflow and register a Python file as its first node
blocks workflow create -n my_workflow -i path/to/functions.py -v 1.0.0

# Run a workflow with input data
blocks workflow run my_workflow -i '{"x": 5}'

# Run multiple workflows independently
blocks workflow run wf_a wf_b -i '{"x": 5}'

# Run a pipeline of workflows (quoted)
blocks workflow run "wf_a > wf_b" -i '{"x": 5}'

# Inspect a workflow (graph + nodes)
blocks workflow info -n my_workflow

# List all workflows in the session directory
blocks workflow list

# List nodes registered inside a workflow
blocks workflow list -n my_workflow

# Add a node to a workflow
blocks workflow add my_node -n my_workflow

# Add a node with a specific bound method
blocks workflow add my_node -n my_workflow -m my_function

# Add a node that does not receive input from the previous node
blocks workflow add my_node -n my_workflow -p

# Add a node whose output is not forwarded to the next node
blocks workflow add my_node -n my_workflow -k

# Add a node with a fixed JSON input sequence
blocks workflow add my_node -n my_workflow -g '{"x": 42}'

# Remove a node from a workflow
blocks workflow del my_node -n my_workflow
```

| `add` option | Description |
|---|---|
| `-p` / `--no-input` | Node does not receive input from previous node |
| `-k` / `--no-output` | Node output is not forwarded to the next node |
| `-g JSON` / `--sequence` | Fixed JSON input passed to this node |

---

## Python API

```python
from blocks import BLOCK_EXEMPLES
from blocks.nodes.node import Node

node = Node.load(name='node_001', directory=BLOCK_EXEMPLES)
node.execute(n=4, delay=0.1)
```

```python
from blocks.nodes.workflow import Workflow

wf = Workflow.load(name='my_workflow', directory='myblock/')
result = wf.execute(x=5)
```

---

## Features

- Multi-language support
- DAG-based workflow execution (acyclic & cyclic graphs)
- Pluggable backends: threads, multiprocessing, distributed, GPU
- In-memory and Redis data buffers
- CLI for workflow and node management

## Usage

See the [documentation](./docs) for more details. (doesn't work yet)



