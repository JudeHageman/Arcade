"""
stack_complexity.py - Analyze time complexity of Stack operations

Measures actual performance of Stack operations and compares to theoretical Big O.

Author: Michael Janeczko
Date: 2/20/2026
Lab: Lab 4 - Time Travel with Stacks
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from stack import Stack
import time
import matplotlib.pyplot as plt


def test_push_time():
    iters = 10
    total_time = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    times = []
    
    print("\nTesting push for time complexity")

    for a in sizes:
        # average over multiple iterations to reduce noise
        for _ in range(iters):
            stack = Stack()
            start = time.perf_counter()
            # push n items onto the stack
            for c in range(a):
                stack.push(c)
            total_time += time.perf_counter() - start
        
        print(f"n: {a}\t Execution time: {total_time / iters:.6f} seconds")
        times.append(total_time / iters)
        total_time = 0
    
    return sizes, times


def test_pop_time():
    iters = 10
    total_time = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    times = []
    
    print("\nTesting pop for time complexity")

    for a in sizes:
        for _ in range(iters):
            # pre-fill the stack before timing
            stack = Stack()
            for c in range(a):
                stack.push(c)
            
            start = time.perf_counter()
            # pop all items and measure time
            for c in range(a):
                stack.pop()
            total_time += time.perf_counter() - start
        
        print(f"n: {a}\t Execution time: {total_time / iters:.6f} seconds")
        times.append(total_time / iters)
        total_time = 0
    
    return sizes, times


def test_push_space():
    iters = 10
    total_peak = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    memory = []

    print("\nTesting push for space complexity")
    
    for a in sizes:
        for _ in range(iters):
            stack = Stack()
            for c in range(a):
                stack.push(c)
            
            # measure size of the underlying array buffer
            total_peak += sys.getsizeof(stack._stack._array)
        
        print(f"n: {a}\t Memory: {(total_peak / iters) / 1e6:.2f} MB")
        memory.append(total_peak / iters)
        total_peak = 0
    
    return sizes, memory


def test_pop_space():
    iters = 10
    total_peak = 0
    sizes = [100, 1000, 10000, 100000, 1000000]
    memory = []
    
    print("\nTesting pop for space complexity")
    
    for a in sizes:
        for _ in range(iters):
            stack = Stack()
            for c in range(a):
                stack.push(c)
            
            total_peak += sys.getsizeof(stack._stack._array)
        
        print(f"n: {a}\t Memory: {(total_peak / iters) / 1e6:.2f} MB")
        memory.append(total_peak / iters)
        total_peak = 0
    
    return sizes, memory


def plot_push_time(sizes, times):
    plt.plot(sizes, times, 'o-', linewidth=1.5, label='Measured push()')
    expected_complexity = [times[0] * (n / sizes[0]) for n in sizes]
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(n)')
    plt.xlabel('n')
    plt.ylabel('average time (seconds)')
    plt.title('Push Time Complexity')
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.savefig('push_time_complexity.png', dpi=200)
    plt.close()


def plot_pop_time(sizes, times):
    plt.plot(sizes, times, 'o-', linewidth=1.5, label='Measured pop()')
    expected_complexity = [times[0] * (n / sizes[0]) for n in sizes]
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(n)')
    plt.xlabel('n')
    plt.ylabel('average time (seconds)')
    plt.title('Pop Time Complexity')
    plt.legend()
    plt.grid(True, alpha=0.5)
    plt.tight_layout()
    plt.savefig('pop_time_complexity.png', dpi=200)
    plt.close()


def plot_push_space(sizes, memory):
    memory_mb = [m / 1e6 for m in memory]
    plt.plot(sizes, memory_mb, 'o-', linewidth=1.5, label='Measured memory')
    expected_complexity = [memory_mb[0] * (n / sizes[0]) for n in sizes]
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(n)')
    
    plt.xlabel('n')
    plt.ylabel('average memory (MB)')
    plt.title('Push Space Complexity')
    plt.legend()
    plt.grid(True, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('push_space_complexity.png', dpi=200)
    plt.close()


def plot_pop_space(sizes, memory):
    memory_mb = [m / 1e6 for m in memory]
    plt.plot(sizes, memory_mb, 'o-', linewidth=1.5, label='Measured memory')
    expected_complexity = [memory_mb[0] * (n / sizes[0]) for n in sizes]
    plt.plot(sizes, expected_complexity, '--', linewidth=1.5, alpha=0.5, label='O(n)')
    
    plt.xlabel('n')
    plt.ylabel('average memory (MB)')
    plt.title('Pop Space Complexity')
    plt.legend()
    plt.grid(True, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('pop_space_complexity.png', dpi=200)
    plt.close()

# run all four benchmarks and generate plots
push_time_sizes, push_times = test_push_time()
pop_time_sizes, pop_times = test_pop_time()
push_space_sizes, push_memory = test_push_space()
pop_space_sizes, pop_memory = test_pop_space()

plot_push_time(push_time_sizes, push_times)
plot_pop_time(pop_time_sizes, pop_times)
plot_push_space(push_space_sizes, push_memory)
plot_pop_space(pop_space_sizes, pop_memory)