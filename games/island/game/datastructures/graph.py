"""
graph.py - Adjacency-list Graph implementation for NPC Dialog Systems.

Author: Minju Seo
Date:   2026-04-21
Lab:    Lab 7 - NPC Dialog with Graphs
"""

from datastructures.hash_table import HashTable


class Graph:
    """
    Adjacency-list graph using HashTable instead of built-in dicts/sets.
    Supports both directed and undirected modes.
    """

    def __init__(self, directed=False):
        """
        Initialize an empty graph.
        Time complexity: O(1)
        """
        self.directed = directed
        self._adj = HashTable()   # node_id -> list of (neighbor_id, weight, edge_data)
        self._data = HashTable()  # node_id -> arbitrary payload
        self._node_count = 0

    def add_node(self, node_id, data=None):
        if not self.has_node(node_id):
            self._adj.set(node_id, [])
            self._data.set(node_id, data)  
            self._node_count += 1
        elif data is not None:
             
            self._data.set(node_id, data)

    def add_edge(self, from_id, to_id, weight=1, edge_data=None):
        """
        Add an edge from from_id to to_id. Creates nodes if they don't exist.
        Time complexity: O(1) average
        """
        if not self.has_node(from_id):
            self.add_node(from_id)
        if not self.has_node(to_id):
            self.add_node(to_id)

        # Add directed edge
        self._adj.get(from_id).append((to_id, weight, edge_data))

        # Add reverse edge if undirected
        if not self.directed:
            self._adj.get(to_id).append((from_id, weight, edge_data))

    def remove_node(self, node_id):
        """
        Remove a node and all edges that touch it.
        Time complexity: O(V + E)
        """
        if not self.has_node(node_id):
            raise KeyError(f"Node {node_id} not found.")

        # 1. Remove the node from the storage
        self._adj.delete(node_id)
        self._data.delete(node_id)
        self._node_count -= 1

        # 2. Search all other nodes to remove incoming edges to node_id
        for other_node in self.nodes():
            edges = self._adj.get(other_node)
            # Filter out edges pointing to node_id
            new_edges = []
            for neighbor_id, weight, data in edges:
                if neighbor_id != node_id:
                    new_edges.append((neighbor_id, weight, data))
            self._adj.set(other_node, new_edges)

    def remove_edge(self, from_id, to_id):
        """
        Remove the edge from from_id to to_id.
        Time complexity: O(degree(from_id))
        """
        if not self.has_node(from_id) or not self.has_node(to_id):
            raise KeyError("One or both nodes do not exist.")

        # Remove from_id -> to_id
        edges = self._adj.get(from_id)
        found = False
        for i, (neighbor, w, d) in enumerate(edges):
            if neighbor == to_id:
                edges.pop(i)
                found = True
                break
        
        if not found:
            raise KeyError(f"Edge from {from_id} to {to_id} not found.")

        # Remove reverse if undirected
        if not self.directed:
            rev_edges = self._adj.get(to_id)
            for i, (neighbor, w, d) in enumerate(rev_edges):
                if neighbor == from_id:
                    rev_edges.pop(i)
                    break

    def get_neighbors(self, node_id):
        """
        Return all edges leaving node_id.
        Time complexity: O(1)
        """
        return self._adj.get(node_id)

    def has_node(self, node_id):
    # HashTable.get이 None을 주면 노드가 없는 것으로 간주
        return self._adj.get(node_id) is not None

    def has_edge(self, from_id, to_id):
        """
        Return True if an edge from_id -> to_id exists.
        Time complexity: O(degree(from_id))
        """
        if not self.has_node(from_id):
            return False
        for neighbor, w, d in self._adj.get(from_id):
            if neighbor == to_id:
                return True
        return False

    def get_node_data(self, node_id):
        # HashTable에서 데이터를 가져옴
        data = self._data.get(node_id)
        
        # 터미널에 실시간 보고 (매우 중요!)
        print(f"--- [Dialog Check] ---")
        print(f"Node ID: '{node_id}'")
        print(f"Retrieved Data: {data}")
        
        if data is None:
            print("결과: 데이터를 못 찾았습니다! (None 반환)")
        elif isinstance(data, dict):
            print(f"결과: 딕셔너리 발견! 텍스트: {data.get('text')}")
        
        return data
    
    def nodes(self):
        """
        Return a list of all node IDs.
        Time complexity: O(V)
        """
        node_list = []
        for node_id, edges in self._adj.items():
            node_list.append(node_id)
        return node_list

    def bfs(self, start_id):
        """
        Breadth-first traversal from start_id.
        Time complexity: O(V + E)
        """
        if not self.has_node(start_id):
            raise KeyError(f"Start node {start_id} not found.")

        order = []
        queue = [start_id]
        visited = HashTable()
        visited.set(start_id, True)

        while queue:
            current = queue.pop(0)
            order.append(current)

            for neighbor, w, d in self.get_neighbors(current):
                # HashTable.get returns None if not found, not KeyError
                if visited.get(neighbor) is None:
                    visited.set(neighbor, True)
                    queue.append(neighbor)
        return order

    def dfs(self, start_id):
        """
        Depth-first traversal from start_id (iterative).
        Time complexity: O(V + E)
        """
        if not self.has_node(start_id):
            raise KeyError(f"Start node {start_id} not found.")

        order = []
        stack = [start_id]
        visited = HashTable()

        while stack:
            current = stack.pop()
            if visited.get(current) is None:
                visited.set(current, True)
                order.append(current)
                
                # To maintain insertion order in DFS, we process neighbors
                # But since it's a stack, the last one pushed is first out.
                for neighbor, w, d in self.get_neighbors(current):
                    stack.append(neighbor)
        return order

    def shortest_path(self, start_id, end_id):
        """
        Find the path with the fewest edges using BFS.
        Time complexity: O(V + E)
        """
        if not self.has_node(start_id) or not self.has_node(end_id):
            raise KeyError("Nodes not found.")

        if start_id == end_id:
            return [start_id]

        visited = HashTable()
        parents = HashTable()
        queue = [start_id]
        visited.set(start_id, True)

        found = False
        while queue:
            current = queue.pop(0)
            if current == end_id:
                found = True
                break

            for neighbor, w, d in self.get_neighbors(current):
                if visited.get(neighbor) is None:
                    visited.set(neighbor, True)
                    parents.set(neighbor, current)
                    queue.append(neighbor)

        if not found:
            return []

        # Reconstruct path
        path = []
        curr = end_id
        while curr != start_id:
            path.append(curr)
            curr = parents.get(curr)
            if curr is None: break # Safety break
        path.append(start_id)
        path.reverse()
        return path

    def __len__(self):
        """Return the number of nodes. Time: O(1)."""
        return self._node_count

    def __str__(self):
        """Return a human-readable summary of the graph."""
        return f"Graph({self._node_count} nodes, directed={self.directed})"