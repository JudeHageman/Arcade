def heap_sort(items, key=lambda value: value, reverse=False):
    """Sort items with a heap and return a new list."""
    values = list(items)
    size = len(values)

    for start in range(size // 2 - 1, -1, -1):
        root = start
        while True:
            child = root * 2 + 1
            if child >= size:
                break

            swap = root
            parent_key = key(values[swap])
            child_key = key(values[child])
            if (reverse and parent_key > child_key) or (not reverse and parent_key < child_key):
                swap = child

            if child + 1 < size:
                right_key = key(values[child + 1])
                swap_key = key(values[swap])
                if (reverse and swap_key > right_key) or (not reverse and swap_key < right_key):
                    swap = child + 1

            if swap == root:
                break

            values[root], values[swap] = values[swap], values[root]
            root = swap

    for end in range(size - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        root = 0
        while True:
            child = root * 2 + 1
            if child >= end:
                break

            swap = root
            parent_key = key(values[swap])
            child_key = key(values[child])
            if (reverse and parent_key > child_key) or (not reverse and parent_key < child_key):
                swap = child

            if child + 1 < end:
                right_key = key(values[child + 1])
                swap_key = key(values[swap])
                if (reverse and swap_key > right_key) or (not reverse and swap_key < right_key):
                    swap = child + 1

            if swap == root:
                break

            values[root], values[swap] = values[swap], values[root]
            root = swap

    return values

