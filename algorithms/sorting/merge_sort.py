def mergesort(items, key=lambda value: value, reverse=False):
    """Sort items by key and return a new list."""
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = mergesort(items[:middle], key=key, reverse=reverse)
    right = mergesort(items[middle:], key=key, reverse=reverse)

    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        left_value = key(left[left_index])
        right_value = key(right[right_index])
        if (left_value <= right_value and not reverse) or (left_value >= right_value and reverse):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged
