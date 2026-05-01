import sys
import os
import time
import random

# Add project root to path to import your Graph
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from datastructures.graph import Graph

def run_benchmark(size):
    """
    Measures the performance of Graph operations for a given number of nodes.
    """
    g = Graph(directed=True)
    nodes = [f"node_{i}" for i in range(size)]
    
    # 1. Measure Build Time (add_node / add_edge)
    start_time = time.perf_counter()
    for node in nodes:
        g.add_node(node)
    # Add roughly 3 edges per node for a realistic density
    for i in range(size):
        for _ in range(3):
            target = random.choice(nodes)
            g.add_edge(nodes[i], target)
    build_time = time.perf_counter() - start_time

    # 2. Measure has_node (1000 random queries)
    start_time = time.perf_counter()
    for _ in range(1000):
        _ = g.has_node(random.choice(nodes))
    has_node_time = time.perf_counter() - start_time

    # 3. Measure BFS
    start_time = time.perf_counter()
    _ = g.bfs(nodes[0])
    bfs_time = time.perf_counter() - start_time

    # 4. Measure DFS
    start_time = time.perf_counter()
    _ = g.dfs(nodes[0])
    dfs_time = time.perf_counter() - start_time

    # 5. Measure shortest_path (10 random pairs)
    start_time = time.perf_counter()
    for _ in range(10):
        start = random.choice(nodes)
        end = random.choice(nodes)
        _ = g.shortest_path(start, end)
    sp_time = time.perf_counter() - start_time

    return {
        "size": size,
        "build": build_time,
        "has_node": has_node_time,
        "bfs": bfs_time,
        "dfs": dfs_time,
        "shortest_path": sp_time
    }

if __name__ == "__main__":
    sizes = [100, 500, 1000]
    results = []

    print(f"{'Size':<10} | {'Build':<10} | {'has_node':<10} | {'BFS':<10} | {'DFS':<10} | {'Shortest'}")
    print("-" * 70)

    for s in sizes:
        res = run_benchmark(s)
        results.append(res)
        print(f"{res['size']:<10} | {res['build']:<10.4f} | {res['has_node']:<10.4f} | {res['bfs']:<10.4f} | {res['dfs']:<10.4f} | {res['shortest_path']:.4f}")

    print("\n### Copy the table below into analysis_write_up.md ###\n")
    print("| Node Size | Build Time (s) | has_node (x1000) | BFS (s) | DFS (s) | Shortest Path (s) |")
    print("|-----------|----------------|-----------------|---------|---------|-------------------|")
    for res in results:
        print(f"| {res['size']:<9} | {res['build']:<14.4f} | {res['has_node']:<15.4f} | {res['bfs']:<7.4f} | {res['dfs']:<7.4f} | {res['shortest_path']:<17.4f} |")