# 🧠 DSA Interview Prep — Complete Explained Notebook (Part 3/3)
## Trie, Heap, Linked List, Matrix, Line Sweep, Hashing & Cheat Sheets

---

# 6. TRIE (Prefix Tree)

### Mental Model

> A tree where each edge = one character. Paths from root to marked nodes spell words. Shared prefixes share paths → space efficient for dictionaries.

```
Insert "apple", "app", "ape":

         root
          │a
          ○
         │p
          ○
       /p    \e
      ○(app✓) ○(ape✓)
      │l
      ○
      │e
      ○(apple✓)
```

---

### Template 1: Trie Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}       # WHY dict? flexible alphabet, no wasted space
        self.is_end = False      # WHY? marks "a complete word ends here"

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()   # WHY? create path if it doesn't exist
            node = node.children[c]
        node.is_end = True                       # WHY? mark this node as a word ending

    def search(self, word):
        node = self.root
        for c in word:
            if c not in node.children: return False  # WHY? path doesn't exist → word not found
            node = node.children[c]
        return node.is_end                            # WHY is_end? "app" is a prefix of "apple", but only a word if marked

    def starts_with(self, prefix):
        node = self.root
        for c in prefix:
            if c not in node.children: return False
            node = node.children[c]
        return True                                   # WHY no is_end check? any prefix is valid
```

**WHY `is_end` matters:**
```
Insert "apple". Then search("app"):
  Path a→p→p exists, but is_end=False → "app" is NOT a word.
  starts_with("app"): path exists → True (it's a valid prefix).

After insert("app"): is_end=True at p→p node → search("app")=True.
```

---

### Template 2: Wildcard Search (WordDictionary)

```python
class WordDictionary:
    def __init__(self): self.root = TrieNode()

    def add_word(self, word):
        node = self.root
        for c in word:
            if c not in node.children: node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def search(self, word):
        def dfs(node, i):
            if i == len(word): return node.is_end
            c = word[i]
            if c == '.':
                return any(dfs(child, i+1) for child in node.children.values())
                # WHY any? '.' matches ANY character → try all children
            if c not in node.children: return False
            return dfs(node.children[c], i+1)
        return dfs(self.root, 0)
```

**WHY DFS for wildcard?** `'.'` can match any single character, so we must explore ALL branches at that position. DFS naturally handles this branching.

**🧠 Memorize:** "Trie = prefix tree. Insert: build path. Search: walk path + check `is_end`. Wildcard: DFS on `'.'`."

---

# 7. HEAP (Priority Queue)

### Mental Model

> Python's `heapq` = **min-heap**. For max-heap, negate values. Heap guarantees O(1) peek at min/max, O(log n) insert/extract.

---

### Template 1: Kth Largest Element

```python
def find_kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k: heapq.heappop(heap)   # WHY? keep only k largest elements
    return heap[0]                                # WHY [0]? smallest of k-largest = kth largest
```

**WHY min-heap of size k?** The heap acts as a filter. Any element smaller than the k-th largest gets popped out. What remains is the top-k, with the smallest at the top.

```
nums=[3,2,1,5,6,4], k=2

Push 3: [3]       size=1 ≤ 2
Push 2: [2,3]     size=2 ≤ 2
Push 1: [1,2,3]   size=3 > 2 → pop 1: [2,3]
Push 5: [2,3,5]   size=3 > 2 → pop 2: [3,5]
Push 6: [3,5,6]   size=3 > 2 → pop 3: [5,6]
Push 4: [4,5,6]   size=3 > 2 → pop 4: [5,6]

heap[0] = 5 = 2nd largest ✅
```

---

### Template 2: Top K Frequent (Bucket Sort)

```python
def top_k_frequent(nums, k):
    count = Counter(nums)
    # WHY bucket sort? O(n) instead of O(n log n) heap
    buckets = [[] for _ in range(len(nums)+1)]     # WHY +1? frequency can be 1..n
    for num, freq in count.items(): buckets[freq].append(num)
    res = []
    for i in range(len(buckets)-1, -1, -1):        # WHY reverse? most frequent first
        res.extend(buckets[i])
        if len(res) >= k: return res[:k]
    return res[:k]
```

**WHY bucket sort over heap?** Frequency is bounded by n (array length). Buckets give O(n) vs heap's O(n log k). In interviews, both are accepted.

---

### Template 3: Median from Data Stream (Two Heaps)

```python
class MedianFinder:
    def __init__(self):
        self.lo = []    # MAX-heap (negate) — lower half
        self.hi = []    # MIN-heap — upper half
        # Invariant: lo holds smaller half, hi holds larger half
        # len(lo) == len(hi) or len(lo) == len(hi)+1

    def add_num(self, num):
        heapq.heappush(self.lo, -num)              # WHY negate? Python only has min-heap
        # Balance values: lo's max must be ≤ hi's min
        if self.hi and -self.lo[0] > self.hi[0]:
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
        # Balance sizes: lo can have at most 1 more than hi
        if len(self.lo) > len(self.hi) + 1:
            heapq.heappush(self.hi, -heapq.heappop(self.lo))
        elif len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self):
        if len(self.lo) > len(self.hi): return -self.lo[0]  # WHY negate? stored negated
        return (-self.lo[0] + self.hi[0]) / 2
```

**WHY two heaps?**
```
            ┌── lo (max-heap) ──┐  ┌── hi (min-heap) ──┐
   smaller numbers ←────── median ──────→ larger numbers

Median = top of lo (if odd count) or average of both tops (if even count).

lo gives largest of smaller half in O(1).
hi gives smallest of larger half in O(1).
Together → median in O(1)!
```

---

### Template 4: Task Scheduler

```python
def least_interval(tasks, n):
    count = Counter(tasks)
    max_count = max(count.values())              # most frequent task's count
    num_max = sum(1 for c in count.values() if c == max_count)  # how many tasks share max frequency
    return max(len(tasks), (max_count - 1) * (n + 1) + num_max)
```

**WHY this formula?** Visualize the schedule:
```
Tasks: A=3, B=3, C=1, n=2

A _ _ A _ _ A      → (max_count-1) chunks of size (n+1) = 2×3 = 6
A B _ A B _ A B    → fill chunks with other tasks
                     + num_max tasks at the end = 2 (A and B)
                     Total = 6 + 2 = 8

But if we have many tasks, no idle slots needed:
  total slots = max(len(tasks), formula_result)
```

---

# 8. LINKED LIST

---

### Template 1: Reverse Linked List

```python
def reverse_list(head):
    prev = None; cur = head             # WHY None? new tail points to None
    while cur:
        nxt = cur.next                  # WHY save? we're about to overwrite it
        cur.next = prev                 # FLIP the arrow ←
        prev = cur; cur = nxt           # advance both pointers
    return prev                          # WHY prev? cur is None (past end), prev is last node
```

**🧠 Memorize:** "Save-Flip-Advance-Advance. Return `prev`."

---

### Template 2: Detect Cycle (Floyd's)

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:           # WHY both checks? fast jumps 2 → could hit None
        slow = slow.next                # 1 step
        fast = fast.next.next           # 2 steps
        if slow == fast: return True    # WHY? in a cycle, fast WILL catch slow
    return False                         # fast reached end → no cycle
```

### Find Cycle Start

```python
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next; fast = fast.next.next
        if slow == fast:
            slow = head                 # WHY reset to head? mathematical proof: distance to start is equal
            while slow != fast:
                slow = slow.next
                fast = fast.next        # WHY both 1-step now? they meet at cycle start
            return slow
    return None
```

**THE MATH:** Let L = distance to cycle start, C = cycle length, K = meeting point offset.
When they meet: `slow = L+K`, `fast = L+K+nC`, and `2(L+K) = L+K+nC` → `L = nC-K`.
So starting one at head and one at meeting point, both going 1-step, they meet at the cycle start.

---

### Template 3: Remove Nth From End

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)           # WHY dummy? handles removing the head node
    fast = slow = dummy
    for _ in range(n+1): fast = fast.next  # WHY n+1? advance fast so slow stops ONE BEFORE target
    while fast:
        fast = fast.next; slow = slow.next
    slow.next = slow.next.next          # WHY? skip the target node
    return dummy.next
```

**WHY `n+1` advance?** We need `slow` to stop at the node BEFORE the target (to rewire `slow.next`). If fast is `n+1` ahead, when fast hits None, slow is exactly 1 before the nth-from-end.

---

### Template 4: Merge Two Sorted Lists

```python
def merge_two_lists(l1, l2):
    dummy = cur = ListNode()           # WHY dummy? avoids special-casing the first node
    while l1 and l2:
        if l1.val <= l2.val: cur.next = l1; l1 = l1.next
        else:                cur.next = l2; l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2                # WHY? append whichever list remains
    return dummy.next                   # WHY .next? skip the placeholder dummy node
```

---

# 9. MATRIX TRAVERSAL

---

### Template 1: Spiral Order

```python
def spiral_order(matrix):
    res = []
    top, bottom, left, right = 0, len(matrix)-1, 0, len(matrix[0])-1
    while top <= bottom and left <= right:
        for c in range(left, right+1): res.append(matrix[top][c])   # → right
        top += 1
        for r in range(top, bottom+1): res.append(matrix[r][right]) # ↓ down
        right -= 1
        if top <= bottom:                                            # WHY check? prevents double-counting single row
            for c in range(right, left-1, -1): res.append(matrix[bottom][c])  # ← left
            bottom -= 1
        if left <= right:                                            # WHY check? prevents double-counting single column
            for r in range(bottom, top-1, -1): res.append(matrix[r][left])    # ↑ up
            left += 1
    return res
```

**WHY the extra `if` checks?** After shrinking `top` and `right`, there might be only a single row or column left. Without checks, we'd traverse it twice (once going right/down, once going left/up).

**🧠 Memorize:** "4 walls shrinking inward: Right→Down→Left→Up. Check before Left/Up."

---

### Template 2: Rotate Image 90° Clockwise

```python
def rotate(matrix):
    n = len(matrix)
    for i in range(n):                                      # TRANSPOSE
        for j in range(i+1, n):                             # WHY i+1? avoid double-swapping
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix: row.reverse()                        # REVERSE each row
```

**WHY transpose + reverse = 90° rotation?**
```
Original:   Transpose:    Reverse rows:
1 2 3       1 4 7         7 4 1
4 5 6  →    2 5 8    →    8 5 2    ← 90° clockwise! ✅
7 8 9       3 6 9         9 6 3
```

---

### Template 3: Search 2D Matrix II (Staircase)

```python
def search_matrix(matrix, target):
    r, c = 0, len(matrix[0]) - 1       # WHY top-right corner? rows increase down, cols decrease left
    while r < len(matrix) and c >= 0:
        if   matrix[r][c] == target: return True
        elif matrix[r][c] > target:  c -= 1     # WHY? current too big → move left (smaller)
        else:                         r += 1    # WHY? current too small → move down (larger)
    return False
```

**WHY top-right corner?** At any position, we can either go **left** (decrease) or **down** (increase). This binary decision eliminates one row or column per step → O(m+n).

---

### Template 4: Set Matrix Zeroes (O(1) Space)

```python
def set_zeroes(matrix):
    nr, nc = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][j]==0 for j in range(nc))  # WHY save? first row is used as flag storage
    first_col_zero = any(matrix[i][0]==0 for i in range(nr))
    for i in range(1, nr):                                     # mark flags
        for j in range(1, nc):
            if matrix[i][j]==0: matrix[i][0]=matrix[0][j]=0   # WHY? use first row/col as markers
    for i in range(1, nr):                                     # apply flags
        for j in range(1, nc):
            if matrix[i][0]==0 or matrix[0][j]==0: matrix[i][j]=0
    if first_row_zero:                                         # WHY last? first row was used as markers
        for j in range(nc): matrix[0][j]=0
    if first_col_zero:
        for i in range(nr): matrix[i][0]=0
```

**WHY use first row/col as markers?** Instead of O(m+n) extra space for "which rows/cols to zero", we store this information IN the matrix itself using the first row and column.

---

# 10. LINE SWEEP

---

### Template 1: Meeting Rooms II (Min Rooms Needed)

```python
def min_meeting_rooms(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))      # WHY +1? meeting starts → need one more room
        events.append((e, -1))     # WHY -1? meeting ends → free one room
    events.sort()                  # WHY sort? process events in chronological order
    rooms = cur = 0
    for _, delta in events:
        cur += delta
        rooms = max(rooms, cur)    # WHY max? peak concurrent meetings = rooms needed
    return rooms
```

**WHY this works:** Convert intervals into point events. Sweep left-to-right, tracking how many meetings are **simultaneously active**. The peak = answer.

```
[[0,30],[5,10],[15,20]]

Events sorted: (0,+1), (5,+1), (10,-1), (15,+1), (20,-1), (30,-1)

cur: 0→1→2→1→2→1→0
          ↑ peak=2 ← answer ✅
```

---

### Template 2: Insert Interval

```python
def insert_interval(intervals, new_interval):
    res = []; i = 0; n = len(intervals)
    while i < n and intervals[i][1] < new_interval[0]:   # WHY? intervals ending before new starts
        res.append(intervals[i]); i += 1                  # → no overlap, keep as-is
    while i < n and intervals[i][0] <= new_interval[1]:   # WHY? overlap condition
        new_interval[0] = min(new_interval[0], intervals[i][0])  # WHY? expand to cover all overlapping
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    res.append(new_interval)                               # WHY? add the merged interval
    while i < n: res.append(intervals[i]); i += 1         # WHY? remaining intervals after new
    return res
```

**🧠 Memorize:** "Three phases: Before (no overlap) → Merge (overlap) → After (no overlap)."

---

# 11. HASHING (Deep Dive)

---

### Template 1: Longest Consecutive Sequence

```python
def longest_consecutive(nums):
    num_set = set(nums); best = 0
    for n in num_set:
        if n - 1 not in num_set:            # WHY? only start counting from SEQUENCE STARTS
            cur = n; length = 1
            while cur + 1 in num_set: cur += 1; length += 1
            best = max(best, length)
    return best
```

**WHY `n-1 not in num_set`?** Without this check, we'd start counting from EVERY element → O(n²). By only starting from numbers that have no predecessor, we count each sequence exactly once → O(n).

```
nums = [100, 4, 200, 1, 3, 2]

100: 99 not in set → start. 101? No. length=1.
4:   3 in set → SKIP (not a sequence start).
200: 199 not in set → start. 201? No. length=1.
1:   0 not in set → start. 2? Yes. 3? Yes. 4? Yes. 5? No. length=4. ✅
3:   2 in set → SKIP.
2:   1 in set → SKIP.
```

---

### Template 2: RandomizedSet (Insert/Remove/GetRandom O(1))

```python
class RandomizedSet:
    def __init__(self):
        self.idx_map = {}    # WHY? val → index for O(1) lookup
        self.vals    = []    # WHY? list for O(1) random access

    def insert(self, val):
        if val in self.idx_map: return False
        self.idx_map[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val):
        if val not in self.idx_map: return False
        i = self.idx_map[val]
        last = self.vals[-1]
        self.vals[i] = last               # WHY swap with last? O(1) removal from list end
        self.idx_map[last] = i            # WHY update? last element moved to index i
        self.vals.pop(); del self.idx_map[val]
        return True

    def get_random(self):
        return random.choice(self.vals)   # WHY list? random.choice needs indexable container
```

**WHY the swap trick?** Removing from the middle of a list is O(n). But removing from the END is O(1). So we swap the target with the last element, then pop the last.

---

# 12. QUICK REFERENCE

---

## Pattern Recognition

| Problem Says | Think This Pattern |
|---|---|
| "sorted array + pair" | **Two Pointers** (opposite ends) |
| "longest/shortest subarray with property" | **Sliding Window** |
| "range sum / prefix query" | **Prefix Sum + HashMap** |
| "max/min K elements" | **Heap** |
| "next greater/smaller" | **Monotonic Stack** |
| "valid brackets / nesting" | **Stack** |
| "connected components" | **BFS/DFS** or **Union-Find** |
| "prerequisites / ordering" | **Topological Sort** |
| "shortest path (weighted)" | **Dijkstra** |
| "prefix matching / autocomplete" | **Trie** |
| "overlapping subproblems" | **DP** |
| "all combinations/permutations" | **Backtracking** |
| "minimum rooms / max overlap" | **Line Sweep** |
| "O(1) membership / grouping" | **HashMap/Set** |

---

## Complexity Cheat Sheet

| Algorithm | Time | Space |
|---|---|---|
| Binary Search | O(log n) | O(1) |
| Two Pointers | O(n) | O(1) |
| Sliding Window | O(n) | O(k) |
| Prefix Sum | O(n) build, O(1) query | O(n) |
| Sorting | O(n log n) | O(n) |
| Monotonic Stack | O(n) | O(n) |
| BFS/DFS | O(V+E) | O(V) |
| Dijkstra | O((V+E) log V) | O(V) |
| Union-Find | O(α) ≈ O(1) | O(V) |
| Topo Sort | O(V+E) | O(V) |
| Heap ops | O(log n) | O(n) |
| Kadane's | O(n) | O(1) |
| Trie ops | O(L) | O(L×σ) |
| 1D DP | O(n) | O(n) or O(1) |
| 2D DP | O(n²) | O(n²) or O(n) |

---

## Interview Communication Checklist

```
1. ✅ Clarify constraints (size, range, edge cases) before coding
2. ✅ State brute force first with its complexity
3. ✅ Explain the optimisation idea before coding it
4. ✅ Code with clean variable names and comments
5. ✅ Walk through a test case manually after coding
6. ✅ State final time and space complexity unprompted
7. ✅ Discuss trade-offs if multiple approaches exist
```

---

## 2-Week Practice Schedule

| Day | Topics | Key Problems |
|---|---|---|
| 1-2 | Two Pointers, Sliding Window, Prefix Sum | LC 3, 209, 560, 11, 15 |
| 3-4 | Sorting, Kadane's, Matrix | LC 56, 53, 152, 62, 221 |
| 5-6 | Monotonic Stack, Stack Design, Heap | LC 739, 84, 42, 215, 295 |
| 7 | Trees: BFS, DFS, BST | LC 102, 543, 236, 124, 98 |
| 8-9 | Graphs: BFS, DFS, Union-Find, Topo | LC 200, 994, 207, 684 |
| 10-11 | DP: 1D, 2D, Knapsack | LC 322, 300, 1143, 416, 72 |
| 12 | Trie, Linked List | LC 208, 206, 141, 23, 25 |
| 13 | Line Sweep, Hashing | LC 253, 128, 380, 49 |
| 14 | **Mock Interview** (2 problems, 60 min) | Random selection |

---

> **This completes the 3-part DSA notebook. All patterns, all templates, all explained.**
