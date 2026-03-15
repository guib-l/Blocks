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

### Workflows

| Command | Description |
|---|---|
| `blocks workflow create` | Create and save a new empty workflow |
| `blocks workflow run` | Load and execute a workflow |
| `blocks workflow info` | Display graph structure and node details |
| `blocks workflow list` | List all workflows in a directory |

**Examples**

```bash
# Create a new workflow
blocks workflow create -n my_workflow -d myblock/
blocks workflow create -n my_workflow -d myblock/ -v 1.0.0

# Run a workflow with input data
blocks workflow run -n my_workflow -d myblock/ -i '{"x": 5}'
blocks workflow run -n my_workflow -d myblock/ -i '{"x": 5}' -f json

# Inspect a workflow
blocks workflow info -n my_workflow -d myblock/

# List all workflows in a directory
blocks workflow list -d myblock/
```

### Nodes

| Command | Description |
|---|---|
| `blocks node run` | Load and execute a node |
| `blocks node info` | Display metadata and registered methods |
| `blocks node list` | List all nodes in a directory |

**Examples**

```bash
# Run a node
blocks node run -n my_node -d myblock/ -m basic_function -i '{"n": 10}'

# Inspect a node
blocks node info -n my_node -d myblock/

# List all nodes in a directory
blocks node list -d myblock/
```

### Miscellaneous

```bash
# Print the installed version
blocks version
```

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


