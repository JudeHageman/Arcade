"""
linked_list_complexity.py - Analyze time complexity of Linked List operations

Measures actual performance of Linked List operations and compares to theoretical Big O.

Author: Michael Janeczko
Date: 4/3/2026
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
from datastructures.patrol_path import PatrolPath
import time
import matplotlib.pyplot as plt


def test_add_waypoint_time():
    """Test time complexity of adding waypoints to patrol path."""
    iters = 10
    total_time = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    times = []
    
    print("\nTesting add_waypoint for time complexity")

    for a in sizes:
        # average over multiple iterations to reduce noise
        for _ in range(iters):
            patrol = PatrolPath("circular")
            start = time.perf_counter()
            # add n waypoints to the patrol path
            for c in range(a):
                patrol.add_waypoint(c * 10, c * 5, wait_time=0)
            total_time += time.perf_counter() - start
        
        print(f"n: {a}\t Execution time: {total_time / iters:.6f} seconds")
        times.append(total_time / iters)
        total_time = 0
    
    return sizes, times


def test_get_next_waypoint_time():
    """Test time complexity of getting next waypoint."""
    iters = 10
    total_time = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    times = []
    
    print("\nTesting get_next_waypoint for time complexity")

    for a in sizes:
        for _ in range(iters):
            # pre-fill the patrol path before timing
            patrol = PatrolPath("circular")
            for c in range(a):
                patrol.add_waypoint(c * 10, c * 5, wait_time=0)
            
            # reset to start of the path before timing
            patrol.reset()
            
            start = time.perf_counter()
            # call get_next_waypoint a times and measure time
            for _ in range(a):
                patrol.get_next_waypoint()
            total_time += time.perf_counter() - start
         
        print(f"n: {a}\t Execution time: {total_time / iters:.6f} seconds")
        times.append(total_time / iters)
        total_time = 0
    
    return sizes, times


def test_add_waypoint_space():
    """Test space complexity of adding waypoints."""
    iters = 10
    total_size = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    memory = []

    print("\nTesting add_waypoint for space complexity")
    
    for a in sizes:
        for _ in range(iters):
            patrol = PatrolPath("circular")
            for c in range(a):
                patrol.add_waypoint(c * 10, c * 5, wait_time=0)
            
            # measure size of patrol path object
            total_size += sys.getsizeof(patrol) + (sys.getsizeof(patrol.head) * patrol.size)
        
        print(f"n: {a}\t Memory: {(total_size / iters) / 1e6:.2f} MB")
        memory.append(total_size / iters)
        total_size = 0
    
    return sizes, memory


def plot_add_waypoint_time(sizes, times):
    """Plot time complexity of add_waypoint."""
    # divide by n to get per-operation time
    per_op_times = [t / n for t, n in zip(times, sizes)]
    plt.plot(sizes, per_op_times, 'o-', linewidth=1.5, label='Measured per-op time')
    # expected is constant for O(1)
    expected_complexity = [per_op_times[-1]] * len(sizes)
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(1) (expected)')
    plt.xlabel('n (number of operations)')
    plt.ylabel('average time per operation (seconds)')
    plt.title('Add Waypoint Time Complexity (O(1) per call)')
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.savefig('add_waypoint_time_complexity.png', dpi=200)
    plt.close()


def plot_get_next_waypoint_time(sizes, times):
    """Plot time complexity of get_next_waypoint."""
    # divide by n to get per-operation time
    per_op_times = [t / n for t, n in zip(times, sizes)]
    plt.plot(sizes, per_op_times, 'o-', linewidth=1.5, label='Measured per-op time')
    # expected is constant for O(1)
    expected_complexity = [per_op_times[-1]] * len(sizes)
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(1) (expected)')
    plt.xlabel('n (number of operations)')
    plt.ylabel('average time per operation (seconds)')
    plt.title('Get Next Waypoint Time Complexity (O(1) per call)')
    plt.ylim(bottom=0)
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.savefig('get_next_waypoint_time_complexity.png', dpi=200)
    plt.close()


def plot_add_waypoint_space(sizes, memory):
    """Plot space complexity of add_waypoint."""
    memory_mb = [m / 1e6 for m in memory]
    plt.plot(sizes, memory_mb, 'o-', linewidth=1.5, label='Measured memory')
    expected_complexity = [memory_mb[0] * (n / sizes[0]) for n in sizes]
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(n)')
    plt.xlabel('n')
    plt.ylabel('average memory (MB)')
    plt.title('Add Waypoint Space Complexity')
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.savefig('add_waypoint_space_complexity.png', dpi=200)
    plt.close()

add_waypoint_time_sizes, add_waypoint_times = test_add_waypoint_time()
get_next_waypoint_time_sizes, get_next_waypoint_times = test_get_next_waypoint_time()
add_waypoint_space_sizes, add_waypoint_memory = test_add_waypoint_space()

plot_add_waypoint_time(add_waypoint_time_sizes, add_waypoint_times)
plot_get_next_waypoint_time(get_next_waypoint_time_sizes, get_next_waypoint_times)
plot_add_waypoint_space(add_waypoint_space_sizes, add_waypoint_memory)