# Written Analysis of Results

## Expected Results
For time complexity, adding a waypoint is expected to be O(1) due to a reference to the tail pointer being maintained, which allows for new nodes to be appended directly to the end of the patrol path, bypassing traversal of the list. Additionally, getting the next waypoint is expected to be O(1) since it advances the current pointer to the node next to it. The space complexity is expected to be O(n) because each new waypoint added requires memory for a node that contains several pieces of data.

## Comparisons
The measured results confirm that adding a waypoint and getting the next waypoint are done in constant time, O(1), which is as expected. Additonally, the space complexity showed linear, O(n), scaling. For example, adding 1,000,000 waypoints consumed 48 MB which is exactly 10 times the memory that was required when adding 100,000 waypoints.

## Discrepancies
There are discrepancies at very small values of n for the time complexity, which is due to execution overhead in Python. The values at larger values of n after the startup costs are much more representative.