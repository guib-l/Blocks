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

The CLI exposes two command groups:

- **`blocks node`** — create, run, inspect and list nodes.
- **`blocks workflow`** — create, run, inspect, list, and edit workflows (add/remove nodes).

Session defaults (author, directory, email) are managed with `blocks config set` and stored in `~/.blocks/session.json`.

See [docs/cli.md](docs/cli.md) for the full command reference.

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



