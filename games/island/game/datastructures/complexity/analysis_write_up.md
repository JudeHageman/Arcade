# Graph Complexity Analysis

**Author:** Minju Seo
**Date:** April 23, 2026
**Lab:** Lab 7 — NPC Dialog with Graphs

---

## 1. Implementation Overview

My Graph implementation uses an **adjacency list** structure, where the underlying storage is a custom **HashTable** instead of Python's built-in dictionaries. In memory, the `_adj` HashTable maps each `node_id` (the key) to a Python list containing tuples of `(neighbor_id, weight, edge_data)`. The implementation is **directed** by default to properly represent the logical flow of NPC conversation states, where one dialog node leads to specific subsequent choices.

---

## 2. Time Complexity Table

| Method            | Your Big-O | Justification (1 sentence each) |
|-------------------|------------|----------------------------------|
| `add_node`        | $O(1)$      | It involves a constant time average insertion into the HashTable to store node data. |
| `add_edge`        | $O(1)$      | It performs constant time lookups to find nodes and appends the edge to the adjacency list. |
| `remove_node`     | $O(V + E)$  | We must delete the node and iterate through every other node's adjacency list to remove incoming edges. |
| `remove_edge`     | $O(deg(V))$ | It requires searching through the specific adjacency list of the source node to find and remove the edge. |
| `has_node`        | $O(1)$      | Checking for a key in the custom HashTable is a constant time operation on average. |
| `has_edge`        | $O(deg(V))$ | It involves searching the adjacency list of the source node for the target neighbor. |
| `get_neighbors`   | $O(1)$      | Retrieving the list of neighbors for a given node ID is a single HashTable lookup. |
| `bfs`             | $O(V + E)$  | The algorithm visits every reachable node and explores every connected edge exactly once. |
| `dfs`             | $O(V + E)$  | Like BFS, it traverses all reachable nodes and edges in linear time relative to graph size. |
| `shortest_path`   | $O(V + E)$  | It utilizes BFS to find the path with the minimum number of edges in unweighted scenarios. |

---

## 3. Benchmark Results

| Node Size | Build Time (s) | has_node (x1000) | BFS (s) | DFS (s) | Shortest Path (s) |
|-----------|----------------|-----------------|---------|---------|-------------------|
| 100       | 0.0039          | 0.0010          | 0.0006  | 0.0006  | 0.0083            |
| 500       | 0.0115          | 0.0026          | 0.0029  | 0.0029  | 0.0393            |
| 1000      | 0.0225          | 0.0010          | 0.0054  | 0.0076  | 0.0544            |

---

## 4. Space Complexity

The space complexity of this implementation is **$O(V + E)$**.
- **$V$ (Vertices):** Represents the number of dialog nodes, each stored as a key in the HashTables.
- **$E$ (Edges):** Represents the total number of player choices (directed edges), each stored as a tuple within the adjacency lists.
Compared to an adjacency matrix ($O(V^2)$), this is much more memory-efficient for the sparse dialog graphs used in the game.

---

## 5. Reflection Questions

**Q1. BFS and DFS both visit every reachable node exactly once. Why might BFS be preferred for `shortest_path` even though both are $O(V + E)$?**

 BFS explores the graph layer by layer, starting from the source node. This ensures that the first time a target node is reached, the path taken is the one with the fewest possible edges. In contrast, DFS might explore deep into a single branch and find a much longer path before ever checking closer neighbors.

---

**Q2. Your adjacency list uses $O(V + E)$ space. An adjacency *matrix* uses $O(V^2)$. For the NPC dialog trees in this lab (small, sparse graphs), which representation is more appropriate? Would your answer change for a 10,000-node social network graph?**

  The adjacency list is more appropriate for dialog trees because most nodes only have a few outgoing choices, making the graph very sparse. For a 10,000-node social network, the adjacency list is even more critical; a matrix would require 100 million entries, most of which would be empty, wasting a massive amount of memory.

---

**Q3. Compare your `bfs` timing to networkx's (if you ran the comparison). What accounts for the difference? Is networkx faster or slower, and why?**

  NetworkX is generally faster because it is a highly optimized library that often uses C backends for its core algorithms. Our custom implementation is written in pure Python and includes the overhead of a manual HashTable implementation, which results in more Python-level operations per node visited.

---

## 6. Conclusions

The implementation performed reliably, showing linear scaling in execution time as the number of nodes increased from 100 to 1000. While the custom HashTable provided efficient $O(1)$ lookups, replacing it with Python's built-in dictionary or optimizing the hashing function could further improve performance. In the game, this Graph structure successfully powers the NPC dialog system, allowing for complex branching conversations and AI-integrated responses.

---

## 7. References

 * *Lab 7 Handout: NPC Dialog with Graphs*
 