import time

class graph_node:

    def __init__(
            self,
            NAME="node-graph-00",
            FROM=None,
            TO=None):
        """Initialize a graph node.

        Args:
            NAME (str): Unique label identifying this node in the graph.
            FROM (list[str] | None): Labels of predecessor nodes (set by
                :meth:`Graphics.set_nodes`).
            TO (list[str] | None): Labels of successor nodes (set by
                :meth:`Graphics.set_nodes`).
        """
        self.NAME = NAME
        self.FROM = FROM
        self.TO   = TO

    def resolve(self, **data):
        """Resolve the next target node(s) given the current execution data.

        The base implementation is a no-op. Subclasses override this method
        to implement conditional routing (:class:`graph_cond`) or loop
        control (:class:`graph_loop`).

        Args:
            **data: Execution payload produced by the current node.
        """
        ...

    def __repr__(self):
        return f" {self.FROM}>({self.NAME})>{self.TO} "


class graph_cond(graph_node):

    def __init__(
            self,
            DEFAULT=None,
            method=None,
            switch=None,
            **kwargs):
        """Initialize a conditional routing node.

        At runtime :meth:`resolve` calls `method` with the execution data
        and compares the result against every value in `switch`. The first
        matching key becomes the next target; if no key matches (or if
        `method` raises), the graph falls back to `DEFAULT`.

        Args:
            DEFAULT (str | None): Label of the fallback successor node used
                when no `switch` branch matches.
            method (Callable | None): Callable invoked with ``**data`` to
                produce the routing value.
            switch (dict | None): Mapping of ``{successor_label: value}``.
                When ``method(**data) == value``, execution is routed to
                ``successor_label``.
            **kwargs: Forwarded to :class:`graph_node` (``NAME``, ``FROM``,
                ``TO``).
        """
        super().__init__(**kwargs)

        self.DEFAULT = DEFAULT #if isinstance(DEFAULT,list) else [DEFAULT]
        self.method = method
        self.switch = switch or {}

    def resolve(self, **data):
        """Route execution to the matching successor or fall back to `DEFAULT`.

        Calls `self.method(**data)`, then iterates over `self.switch` to find
        a value equal to the result. Updates :attr:`TO` in-place. If `method`
        is ``None``, raises, or no branch matches, :attr:`TO` is set to
        ``[self.DEFAULT]``.

        Args:
            **data: Execution payload forwarded to `self.method`.
        """
        try:
            if self.method is not None and self.switch is not None:
                results = self.method(**data)
                for key,item in self.switch.items():
                    if item==results:
                        self.TO = [key]
                        return

            self.TO = [ self.DEFAULT ]
        except Exception as e:
            self.TO = [ self.DEFAULT ]


class graph_loop(graph_node):

    def __init__(
            self,
            RETURN=None,
            epoch=1,
            method=None,
            switch=None,
            **kwargs):
        """Initialize a loop control node.

        Each call to :meth:`resolve` decrements the epoch counter. Once the
        counter reaches zero the loop exits by redirecting :attr:`TO` to
        `RETURN`.

        Args:
            RETURN (str | None): Label of the node to jump to when the loop
                ends (epoch exhausted).
            epoch (int): Number of iterations to execute before exiting.
            method (Callable | None): Reserved for future conditional exit
                logic.
            switch (dict | None): Reserved for future conditional exit
                logic.
            **kwargs: Forwarded to :class:`graph_node` (``NAME``, ``FROM``,
                ``TO``).
        """
        super().__init__(**kwargs)

        self.RETURN = RETURN
        self.epoch = epoch
        self.method = method
        self.switch = switch or {}

    def resolve(self, **data):
        """Decrement the epoch counter and exit the loop when exhausted.

        While ``self.epoch > 0`` the node keeps its current :attr:`TO`
        (i.e. loops back). When the counter reaches zero :attr:`TO` is
        replaced with ``self.RETURN`` to continue linear execution.

        Args:
            **data: Execution payload (not used by the base implementation).
        """
        self.epoch -= 1
        if self.epoch <= 0:
            self.TO = self.RETURN

    

class Graphics:

    def __init__(
            self,
            links=None,
            first=None,
            last=None,
            allow_cycles=False):
        """Initialize a graph.

        Args:
            links (list[tuple[str, str]] | None): Initial edges as
                ``(src, dst)`` pairs. Each unique label found in the pairs
                becomes a :class:`graph_node`.
            first (str | None): Label of the entry node. Inferred
                automatically from the first edge when ``None``.
            last (str | None): Label of the exit node.
            allow_cycles (bool): When ``False`` (default), subclasses
                such as :class:`blocks.engine.oriented.AcyclicGraphic`
                may reject cyclic graphs during traversal.
        """
        
        self.links = []
        self.first = first
        self.last  = last

        self.nodes      = {}
        self.nodes_type = {}

        self.add_links(links)

        self.allow_cycles = allow_cycles

    @property
    def first(self):
        """str | None: Label of the graph entry node."""
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @property
    def last(self):
        """str | None: Label of the graph exit node."""
        return self._last

    @last.setter
    def last(self, value):
        self._last = value

    # ========================= Link Manipulation Methods =========================
    # Methods to add/remove links, and to query the graph structure.


    def add_link(self, src, dst, node=True):
        """Add a directed edge from `src` to `dst`.

        Both node labels are registered in :attr:`nodes_type` as plain
        :class:`graph_node` entries (if not already present). When `src` is
        the first edge added, :attr:`first` is set automatically.

        Args:
            src (str): Label of the source node.
            dst (str): Label of the destination node.
            node (bool): When ``True`` (default), :meth:`set_nodes` is called
                immediately to rebuild the in-memory node objects. Pass
                ``False`` when adding many edges in bulk and call
                :meth:`set_nodes` manually afterwards.
        """
        if (src,dst) not in self.links:
            self.links.append((src,dst))
        
        self.nodes_type.update(
            {
                src:{
                    'type':graph_node,
                     'args':{}},
                dst:{
                    'type':graph_node,
                     'args':{}}
            }
        )
        if self.first is None:
            self.first = src

        if node:
            self.set_nodes()

    def add_links(self, links):
        """Add multiple directed edges at once.

        Defers :meth:`set_nodes` until all edges are registered, making
        bulk insertion more efficient than repeated :meth:`add_link` calls.

        Args:
            links (list[tuple[str, str]] | None): Edges as ``(src, dst)``
                pairs. A ``None`` value is silently ignored.
        """
        if links is None:
            return
        for link in links:
            self.add_link(link[0], link[1], node=False)

        self.set_nodes()
    
    def del_link(self, src, dst):
        if (src,dst) in self.links:
            self.links.remove((src,dst))
            self.set_nodes()

    def del_links(self, links):
        """Remove multiple directed edges at once.

        Args:
            links (list[tuple[str, str]]): Edges as ``(src, dst)`` pairs.
        """
        for link in links:
            self.del_link(link[0], link[1])

    def linked_to(self, node):
        return {
            'node': node,
            'prev': [src for src,dst in self.links if dst==node],
            'next': [dst for src,dst in self.links if src==node],
        }

    def required_nodes(self):
        """Return the set of all node labels referenced by at least one edge.

        Returns:
            set[str]: Union of all source and destination labels across
            :attr:`links`.
        """
        return set(
            [src for src,_ in self.links] + 
            [dst for _,dst in self.links])

    # ========================= Node Manipulation Methods =========================
    # Methods to add/remove nodes, and to query the graph structure.

    def set_nodes(self):

        keys = set(
            [src for src,_ in self.links] + 
            [dst for _,dst in self.links])

        for node in keys:
            ARL = [src for src,dst in self.links \
                        if dst==node and src in keys]
            DST = [dst for src,dst in self.links \
                        if src==node and dst in keys]
            
            objt = self.nodes_type[node]['type']
            args = self.nodes_type[node]['args']

            self.nodes.update(
                {
                    node:objt(
                        NAME=node,
                        FROM=ARL,
                        TO=DST,
                        **args)
                }
            )

    def del_node(self, node):
        if node in self.nodes:
            del self.nodes[node]
            del self.nodes_type[node]
            self.del_links(
                [(src,dst) for src,dst in self.links \
                    if src==node or dst==node]
            )

    def to_config(self):
        """Serialize the graph structure into a configuration dictionary.

        The returned mapping can be passed directly to the constructor to
        reconstruct an equivalent graph.

        Returns:
            dict: A dictionary with keys ``'links'``, ``'first'``,
            and ``'last'``.
        """
        return {
            'links': self.links,
            'first': self.first,
            'last' : self.last,
        }









