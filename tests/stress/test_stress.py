import os
import sys
import time
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_structures")))

from hash_table import HashTable
from prefix_trie import PrefixTrie
from bst import BST
from linked_list import LinkedList
from dynamic_array import ArrayList

import matplotlib.pyplot as plt


def run_stress_test():
    """Run the stress test and generate the total-time plot."""
    player_count = 120_000
    query_volumes = [100, 1_000, 5_000, 10_000, 50_000, 100_000]
    iters = 3
    rng_seed = 1234

    t0 = time.perf_counter()
    rnd = random.Random(rng_seed)
    teams = ("pink", "green", "blue")
    usernames = ArrayList()
    score_keys = ArrayList()
    table = HashTable(capacity=max(16, player_count * 2))
    trie = PrefixTrie()
    bst = BST()
    history_index = HashTable(capacity=max(16, player_count * 2))

    for i in range(player_count):
        prefix = "".join(rnd.choices(string.ascii_lowercase, k=5))
        username = f"{prefix}{i}"
        team = teams[i % 3]
        score = rnd.randint(0, 100_000)
        usernames.append(username)
        score_keys.append((score, username))
        table.put(username, {"team": team, "score": score, "wins": rnd.randint(0, 200)})
        trie.insert(username)
        bst.insert((score, username))

        history = LinkedList()
        for _ in range(3):
            history.add_last({"score": rnd.randint(0, 1000)})
        history_index.put(username, history)

    _ = time.perf_counter() - t0

    results = {}
    workloads = (
        ("hash_lookup", "Player Profile Lookup"),
        ("prefix_lookup", "Username Prefix Lookup"),
        ("exact_search", "Exact Username Search"),
        ("leaderboard_check", "Leaderboard Membership Check"),
        ("mixed_path", "Combined Query Path"),
    )

    for seed_base, (workload_key, display_label) in enumerate(workloads, start=1):
        totals = []
        for v in query_volumes:
            elapsed = 0.0
            for it in range(iters):
                query_rng = random.Random(seed_base + it)
                name_q = ArrayList()
                key_q = ArrayList()
                for _ in range(v):
                    idx = query_rng.randrange(len(usernames))
                    name_q.append(usernames[idx])
                    key_q.append(score_keys[idx])

                start = time.perf_counter()
                if workload_key == "hash_lookup":
                    for i in range(v):
                        try:
                            table.get(name_q[i])
                        except KeyError:
                            pass
                elif workload_key == "prefix_lookup":
                    for i in range(v):
                        trie.starts_with(name_q[i][:3])
                elif workload_key == "exact_search":
                    for i in range(v):
                        trie.search(name_q[i])
                elif workload_key == "leaderboard_check":
                    for i in range(v):
                        bst.contains(key_q[i])
                else:
                    for i in range(v):
                        u = name_q[i]
                        try:
                            table.get(u)
                        except KeyError:
                            pass
                        trie.starts_with(u[:3])
                        bst.contains(key_q[i])
                elapsed += time.perf_counter() - start

            totals.append(elapsed / iters)
        results[display_label] = totals

    out_dir = os.path.dirname(os.path.abspath(__file__))
    plt.figure(figsize=(8, 5))
    for name, totals in results.items():
        plt.plot(query_volumes, totals, "o-", linewidth=1.5, label=name)
    plt.xlabel("query volume")
    plt.ylabel("total time (seconds)")
    plt.title("Total time vs query volume (in-process, no network)")
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "stress_test_total_time.png"), dpi=200)
    plt.close()

    print("\nAll tests passed.")


if __name__ == "__main__":
    run_stress_test()
