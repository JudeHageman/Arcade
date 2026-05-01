"""
dialog_graph.py - Conversation tree built on top of Graph

This file is PROVIDED. Do not modify it.

A DialogGraph wraps your Graph to represent NPC conversation trees.
Each node is a dialog "state" (what the NPC says at that point).
Each directed edge is a player choice that leads to the next state.

If your Graph raises NotImplementedError, DialogGraph falls back to a
simple dict-based implementation so the game still runs during development.
"""


class DialogGraph:
    """
    Directed conversation tree for an NPC.

    Node data : {"text": str, "type": "fixed" | "ai" | "end"}
    Edge data : player's choice text (str)

    Typical usage
    -------------
        dg = DialogGraph("Merchant")
        dg.add_dialog_node("hello", "What are you buying?")
        dg.add_dialog_node("bye",   "Come again!", node_type="end")
        dg.add_choice("hello", "bye", "Nothing, goodbye.")
        dg.set_start("hello")
    """

    def __init__(self, npc_name="NPC"):
        self.npc_name = npc_name
        self._start   = None
        self._current = None
        self._graph   = self._make_graph()

    def _make_graph(self):
        """Build a directed Graph, with a dict-based fallback."""
        try:
            from datastructures.graph import Graph
            g = Graph(directed=True)
            # Smoke-test the required interface
            g.add_node("__smoke__")
            g.add_edge("__smoke__", "__smoke__")
            g.has_node("__smoke__")
            g.get_neighbors("__smoke__")
            g.remove_node("__smoke__")
            return g
        except Exception:
            return _FallbackGraph()

    def add_dialog_node(self, node_id, text, node_type="fixed"):
        """
        Add a dialog state (node).

        Args:
            node_id  : Unique string key (e.g. "greet", "quest_offer").
            text     : What the NPC says when this state is reached.
            node_type: "fixed"  — static pre-written text (default).
                       "ai"     — Gemini generates the response at runtime.
                       "end"    — conversation closes after showing this text.
        """
        self._graph.add_node(node_id, data={"text": text, "type": node_type})

    def add_choice(self, from_id, to_id, choice_text):
        """
        Add a directed edge representing one player choice.

        Args:
            from_id    : Source dialog node.
            to_id      : Destination dialog node.
            choice_text: Text shown to the player as a numbered option.
        """
        self._graph.add_edge(from_id, to_id, edge_data=choice_text)

    def set_start(self, node_id):
        """Set the opening node.  Call once after building the tree."""
        self._start   = node_id
        self._current = node_id

    def reset(self):
        """Restart the conversation from the beginning."""
        self._current = self._start

    def get_current_text(self):
        """Return the NPC's text for the current dialog state."""
        if not self._graph.has_node(self._current):
            return "(No dialog)"
        data = self._graph.get_node_data(self._current)
        return data["text"] if data else "(No text)"

    def get_current_type(self):
        """Return 'fixed', 'ai', or 'end' for the current state."""
        if not self._graph.has_node(self._current):
            return "end"
        data = self._graph.get_node_data(self._current)
        return data.get("type", "fixed") if data else "end"

    def get_choices(self):
        """
        Return available player choices at the current state.

        Returns:
            list of (choice_text, to_node_id) tuples in insertion order.
        """
        if not self._graph.has_node(self._current):
            return []
        return [
            (edge_data, neighbor_id)
            for neighbor_id, weight, edge_data
            in self._graph.get_neighbors(self._current)
            if edge_data is not None
        ]

    def choose(self, choice_index):
        """
        Traverse to the next state via a player choice.

        Args:
            choice_index: 0-based index into get_choices().

        Returns:
            True if traversal succeeded, False for invalid index.
        """
        choices = self.get_choices()
        if 0 <= choice_index < len(choices):
            _, next_node = choices[choice_index]
            self._current = next_node
            return True
        return False

    def is_ended(self):
        """True when the current node is an end node or has no choices."""
        return self.get_current_type() == "end" or len(self.get_choices()) == 0


class _FallbackGraph:
    """Minimal dict-backed directed graph."""

    def __init__(self):
        self._nodes = {}
        self._edges = {}

    def add_node(self, node_id, data=None):
        if node_id not in self._nodes:
            self._nodes[node_id] = data
            self._edges[node_id] = []
        else:
            self._nodes[node_id] = data

    def add_edge(self, from_id, to_id, weight=1, edge_data=None):
        self.add_node(from_id)
        self.add_node(to_id)
        self._edges[from_id].append((to_id, weight, edge_data))

    def remove_node(self, node_id):
        del self._nodes[node_id]
        del self._edges[node_id]
        for k in self._edges:
            self._edges[k] = [
                (n, w, d) for n, w, d in self._edges[k] if n != node_id
            ]

    def has_node(self, node_id):
        return node_id in self._nodes

    def get_neighbors(self, node_id):
        return list(self._edges.get(node_id, []))

    def get_node_data(self, node_id):
        return self._nodes.get(node_id)
