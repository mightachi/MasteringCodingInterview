# 🧠 DSA Interview Prep — Notebook Supplement
## Backtracking & Bit Manipulation/Masking

---

# 13. BACKTRACKING

---

### Mental Model

> **Backtracking = DFS on a Decision Tree.** At each level, make a choice. If it leads to a dead end, UNDO the choice (backtrack) and try the next option.

```
Universal Template:

def backtrack(path, choices):
    if goal_reached(path):
        result.append(path[:])    ← save a COPY
        return
    for choice in choices:
        if is_valid(choice):      ← prune
            path.append(choice)   ← CHOOSE
            backtrack(path, ...)  ← EXPLORE
            path.pop()            ← UN-CHOOSE (backtrack)
```

**The 3 Steps:** CHOOSE → EXPLORE → UN-CHOOSE. This is the heartbeat of every backtracking solution.

### Decision Framework

| Problem Type | How to Identify | Key Difference |
|---|---|---|
| **Subsets** | "all subsets", "power set" | Include/exclude each element |
| **Permutations** | "all arrangements", "order matters" | Visited set, no start index |
| **Combinations** | "choose k from n", "order doesn't matter" | Start index moves forward |
| **Constraint satisfaction** | "place N queens", "solve sudoku" | Validity check before placing |

---

### Template 1: Subsets (LC #78)

```python
def subsets(nums):
    result = []
    def backtrack(start, path):
        result.append(path[:])               # WHY copy? path is mutable, will change later
        for i in range(start, len(nums)):    # WHY start? prevents duplicates like [1,2] and [2,1]
            path.append(nums[i])             # CHOOSE
            backtrack(i + 1, path)           # EXPLORE (i+1: don't reuse same element)
            path.pop()                       # UN-CHOOSE
    backtrack(0, [])
    return result
```

**WHY `result.append(path[:])`?** `path` is a reference. Without copying, all entries in `result` would point to the same (eventually empty) list.

**WHY record at EVERY node (not just leaves)?** Subsets include ALL sizes: `[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]`.

**Decision Tree:**
```
nums = [1, 2, 3]

                    []
            /        |        \
         [1]        [2]       [3]
        /    \       |
     [1,2]  [1,3]  [2,3]
       |
    [1,2,3]

Every node is a valid subset → 8 results (2³) ✅
```

**Dry Run:**
```
backtrack(0, [])
  result: [[]]
  i=0: path=[1]
    backtrack(1, [1])
      result: [[], [1]]
      i=1: path=[1,2]
        backtrack(2, [1,2])
          result: [[], [1], [1,2]]
          i=2: path=[1,2,3]
            backtrack(3, [1,2,3])
              result: [[], [1], [1,2], [1,2,3]]
            path.pop() → [1,2]
        path.pop() → [1]
      i=2: path=[1,3]
        backtrack(3, [1,3])
          result: [..., [1,3]]
        path.pop() → [1]
    path.pop() → []
  i=1: path=[2]
    ... and so on
```

---

### Template 2: Permutations (LC #46)

```python
def permutations(nums):
    result = []
    def backtrack(path, used):
        if len(path) == len(nums):           # WHY? permutation uses ALL elements
            result.append(path[:])
            return
        for i in range(len(nums)):           # WHY from 0? order matters, any unused element can go next
            if used[i]: continue             # WHY? each element used exactly once
            used[i] = True                   # CHOOSE
            path.append(nums[i])
            backtrack(path, used)            # EXPLORE
            path.pop()                       # UN-CHOOSE
            used[i] = False
    backtrack([], [False]*len(nums))
    return result
```

**WHY `used` array instead of `start` index?** In subsets/combinations, order doesn't matter → use `start` to enforce forward-only selection. In permutations, order matters → any unused element can go at any position → need `used` flags.

**WHY loop from 0 (not from start)?** `[2,1]` and `[1,2]` are DIFFERENT permutations. Must consider all unused elements at each position.

---

### Template 3: Combination Sum (LC #39)

```python
def combination_sum(candidates, target):
    result = []
    def backtrack(start, path, remaining):
        if remaining == 0:                   # WHY? found exact target sum
            result.append(path[:])
            return
        if remaining < 0: return             # WHY? overshot → prune this branch
        for i in range(start, len(candidates)):  # WHY start? avoid [2,3] and [3,2] duplicates
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # WHY i (not i+1)? elements CAN be reused
            path.pop()
    backtrack(0, [], target)
    return result
```

**WHY `i` instead of `i+1`?** "Each number may be used unlimited number of times." Passing `i` allows re-selecting the same element.

**WHY `remaining < 0` prune?** Without it, we'd keep adding forever. This cuts dead branches early.

**Decision Tree for `candidates=[2,3,6,7], target=7`:**
```
                     target=7
                /      |      \       \
            2(5)    3(4)    6(1)    7(0)✅
           / | \     / \      |
        2(3) 3(2) 6 2(1) 3   6(-5)✗
        /|   /\      |
     2(1)3 2(0)✅  3(-2)✗
      |
    2(-1)✗
```

---

### Template 4: N-Queens (LC #51)

```python
def solve_n_queens(n):
    result = []
    board = [['.']*n for _ in range(n)]
    cols = set()          # WHY sets? O(1) lookup for column/diagonal conflicts
    diag1 = set()         # WHY diag1? cells on same diagonal: row-col = constant
    diag2 = set()         # WHY diag2? cells on same anti-diagonal: row+col = constant
    
    def backtrack(row):
        if row == n:                            # WHY? all rows filled → valid solution
            result.append([''.join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row-col) in diag1 or (row+col) in diag2:
                continue                        # WHY? queen would be attacked → skip
            board[row][col] = 'Q'               # CHOOSE
            cols.add(col); diag1.add(row-col); diag2.add(row+col)
            backtrack(row + 1)                  # EXPLORE (next row)
            board[row][col] = '.'               # UN-CHOOSE
            cols.remove(col); diag1.remove(row-col); diag2.remove(row+col)
    
    backtrack(0)
    return result
```

**WHY process row by row?** Each row must have exactly one queen. By placing one queen per row, we automatically avoid row conflicts.

**WHY `row - col` for diagonals?** On any `\` diagonal, `row - col` is constant:
```
  0 1 2 3
0 [0,-1,-2,-3]
1 [1, 0,-1,-2]
2 [2, 1, 0,-1]    row-col values
3 [3, 2, 1, 0]
```

**WHY `row + col` for anti-diagonals?** On any `/` diagonal, `row + col` is constant:
```
  0 1 2 3
0 [0, 1, 2, 3]
1 [1, 2, 3, 4]    row+col values
2 [2, 3, 4, 5]
3 [3, 4, 5, 6]
```

---

### Backtracking With Duplicate Input (LC #90: Subsets II)

```python
def subsets_with_dup(nums):
    nums.sort()                                  # WHY sort? groups duplicates together for skipping
    result = []
    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i-1]: continue  # WHY? skip duplicate at SAME level
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result
```

**WHY `i > start` (not `i > 0`)?** We only skip duplicates at the **same decision level**. The first occurrence at each level is allowed; subsequent identical values are skipped.

---

### 🧠 Memorize

> **"Choose-Explore-Unchoose."**
> - **Subsets:** record at every node, start index, no reuse
> - **Permutations:** record at leaves only, used array, loop from 0
> - **Combinations:** record when target met, start index, `i` (reuse) or `i+1` (no reuse)
> - **Constraints:** prune with sets/checks before choosing

### Common Mistakes

| Mistake | Fix |
|---|---|
| Not copying path: `result.append(path)` | Use `path[:]` or `list(path)` |
| Using `start` for permutations | Use `used` array (order matters) |
| Not sorting before duplicate handling | Sort first, then skip `nums[i]==nums[i-1]` |
| `i > 0` for duplicate skip in subsets | Use `i > start` (only at same decision level) |
| Forgetting to un-choose (pop, reset) | Always undo: `path.pop()`, `used[i]=False`, etc. |

### Practice Problems

| # | Problem | Difficulty | Type |
|---|---|---|---|
| LC 78 | Subsets | 🟡 | include/exclude |
| LC 90 | Subsets II (duplicates) | 🟡 | sort + skip |
| LC 46 | Permutations | 🟡 | used array |
| LC 39 | Combination Sum | 🟡 | reuse allowed |
| LC 40 | Combination Sum II | 🟡 | no reuse + skip dups |
| LC 51 | N-Queens | 🔴 | constraint placement |
| LC 37 | Sudoku Solver | 🔴 | constraint propagation |
| LC 79 | Word Search | 🟡 | grid backtracking |
| LC 131 | Palindrome Partitioning | 🟡 | partition + check |

---

# 14. BIT MANIPULATION & BITMASK DP

---

### Mental Model

> Bits are the **lowest-level** building blocks. Mastering bit operations gives you O(1) tricks that replace loops, and **bitmask DP** lets you encode "which items are selected" in a single integer.

---

## Core Bit Operations Cheat Sheet

```python
# ── Essential Bit Operations ─────────────────────────────────────────
a & b       # AND: both bits 1 → 1.     Use: check if bit is set
a | b       # OR:  either bit 1 → 1.    Use: set a bit
a ^ b       # XOR: different bits → 1.  Use: find unique, toggle
~a          # NOT: flip all bits.        Use: complement
a << n      # left shift: multiply by 2ⁿ
a >> n      # right shift: divide by 2ⁿ
```

### Bit Tricks Reference

```python
# Check if bit i is set
(n >> i) & 1                    # WHY? shift bit i to position 0, mask with 1

# Set bit i
n | (1 << i)                    # WHY? 1<<i has only bit i set, OR turns it on

# Clear bit i
n & ~(1 << i)                   # WHY? ~(1<<i) has all bits set EXCEPT i, AND clears it

# Toggle bit i
n ^ (1 << i)                    # WHY? XOR with 1 flips the bit

# Check power of 2
n > 0 and (n & (n-1)) == 0     # WHY? power of 2 has exactly one bit set;
                                 # n-1 flips all lower bits; AND gives 0

# Count set bits (Kernighan's)
count = 0
while n:
    n &= n - 1                  # WHY? clears the LOWEST set bit each time
    count += 1

# Lowest set bit
n & (-n)                        # WHY? -n = ~n+1, only the lowest set bit survives AND

# XOR properties (THE most important):
# a ^ a = 0       (self-cancels)
# a ^ 0 = a       (identity)
# a ^ b ^ a = b   (cancellation extracts b)
```

---

### Template 1: Single Number (LC #136) — XOR Magic

```python
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x           # WHY? pairs cancel: a^a=0. The lone number survives.
    return result
```

**WHY XOR?** Every number appearing twice cancels itself (`a^a=0`). What remains is the single unique number.

```
nums = [4, 1, 2, 1, 2]

result = 0
0 ^ 4 = 4
4 ^ 1 = 5
5 ^ 2 = 7
7 ^ 1 = 6     ← 1 cancels
6 ^ 2 = 4     ← 2 cancels

Result: 4 ✅ (the only number appearing once)
```

**O(n) time, O(1) space** — no hashmap needed!

---

### Template 2: Number of 1 Bits / Counting Bits

```python
# Count bits in one number (Kernighan's trick)
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1            # WHY? clears lowest set bit. Runs exactly (num_of_1s) times.
        count += 1
    return count
```

**WHY `n & (n-1)` clears the lowest set bit:**
```
n   = 12 = 1100
n-1 = 11 = 1011
n & (n-1) = 1000 = 8  ← removed the lowest '1' at position 2

n   =  8 = 1000
n-1 =  7 = 0111
n & (n-1) = 0000 = 0  ← removed the last '1'

Iterations: 2 (12 has two set bits) ✅
```

```python
# Count bits for all numbers 0..n (LC #338)
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)   # WHY? bits(i) = bits(i/2) + last_bit
    return dp
```

**WHY `dp[i>>1] + (i&1)`?** Shifting right removes the last bit. The remaining bits = `dp[i>>1]`. Add back the removed bit: `i & 1`.

```
i=6 (110): dp[3] + 0 = dp[3] + 0.  dp[3]=dp[1]+1=2. dp[6]=2 ✅ (110 has 2 bits)
i=7 (111): dp[3] + 1 = 2 + 1 = 3 ✅ (111 has 3 bits)
```

---

### Template 3: Power of Two

```python
def is_power_of_two(n):
    return n > 0 and (n & (n-1)) == 0
    # WHY? powers of 2 have exactly ONE bit set.
    # n & (n-1) clears that one bit → result is 0.
```

```
n=8: 1000 & 0111 = 0000 → True ✅
n=6: 0110 & 0101 = 0100 → not 0 → False ✅
n=0: fails n>0 → False ✅ (0 is not a power of 2)
```

---

### Template 4: Subsets Using Bitmask (Alternative to Backtracking)

```python
def subsets_bitmask(nums):
    n = len(nums)
    result = []
    for mask in range(1 << n):            # WHY 1<<n? there are 2ⁿ subsets
        subset = []
        for i in range(n):
            if mask & (1 << i):           # WHY? check if element i is "selected" in this mask
                subset.append(nums[i])
        result.append(subset)
    return result
```

**WHY bitmask for subsets?** Each subset maps to a binary number where bit `i` = "include element i":

```
nums = [a, b, c]

mask=000 (0): []
mask=001 (1): [a]          bit 0 set → include nums[0]
mask=010 (2): [b]          bit 1 set → include nums[1]
mask=011 (3): [a,b]        bits 0,1 set
mask=100 (4): [c]
mask=101 (5): [a,c]
mask=110 (6): [b,c]
mask=111 (7): [a,b,c]      all bits set → all elements
```

---

### Template 5: Bitmask DP — Travelling Salesman (TSP)

```python
def tsp(dist):
    """Find shortest route visiting all n cities exactly once and returning to start."""
    n = len(dist)
    ALL = (1 << n) - 1                    # WHY? binary 111...1 = all cities visited
    
    # dp[mask][i] = min cost to reach city i, having visited cities in mask
    dp = [[float('inf')] * n for _ in range(1 << n)]
    dp[1][0] = 0                          # WHY? start at city 0, only city 0 visited (mask=0001)
    
    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u] == float('inf'): continue
            if not (mask & (1 << u)): continue  # WHY? u must be IN the visited set
            for v in range(n):
                if mask & (1 << v): continue    # WHY? v must NOT be visited yet
                new_mask = mask | (1 << v)      # WHY? mark v as visited
                dp[new_mask][v] = min(dp[new_mask][v], dp[mask][u] + dist[u][v])
    
    # Return to city 0 from any final city
    return min(dp[ALL][i] + dist[i][0] for i in range(1, n))
```

**WHY bitmask for TSP?** We need to track "which cities have been visited." With n cities, there are 2ⁿ possible subsets. A bitmask encodes any subset as a single integer → use as array index.

**State:** `dp[mask][i]` = minimum cost to reach city `i`, having visited exactly the cities represented by `mask`.

**Transition:** From city `u` with visited set `mask`, go to unvisited city `v`:
```
dp[mask | (1<<v)][v] = min(dp[mask | (1<<v)][v], dp[mask][u] + dist[u][v])
```

**Complexity:** O(2ⁿ × n²) time, O(2ⁿ × n) space. Works for n ≤ 20.

---

### Template 6: Minimum XOR Sum of Two Arrays (Bitmask DP)

```python
def minimum_xor_sum(nums1, nums2):
    n = len(nums1)
    dp = [float('inf')] * (1 << n)
    dp[0] = 0                                  # WHY? no elements paired yet → cost 0
    
    for mask in range(1 << n):
        i = bin(mask).count('1')               # WHY? number of bits set = how many elements from nums1 paired so far
        if i >= n: continue
        for j in range(n):
            if mask & (1 << j): continue       # WHY? nums2[j] already used
            new_mask = mask | (1 << j)
            dp[new_mask] = min(dp[new_mask], dp[mask] + (nums1[i] ^ nums2[j]))
    
    return dp[(1 << n) - 1]                    # WHY? all of nums2 used
```

**WHY bitmask here?** We're assigning each element of `nums2` to exactly one element of `nums1`. The bitmask tracks which elements of `nums2` have been used.

---

### Bit Manipulation Common Tricks Summary

```
╔══════════════════════════════╦══════════════════╦═══════════════════════╗
║ Want to...                   ║ Operation         ║ Example               ║
╠══════════════════════════════╬══════════════════╬═══════════════════════╣
║ Find unique in pairs         ║ XOR all           ║ a^a=0, b survives     ║
║ Check if power of 2          ║ n & (n-1) == 0    ║ 8: 1000 & 0111 = 0    ║
║ Count set bits               ║ n &= n-1 loop     ║ 12→8→0 = 2 bits      ║
║ Get lowest set bit           ║ n & (-n)           ║ 12: 1100 & 0100 = 4  ║
║ Enumerate all subsets        ║ for m in 0..2ⁿ-1   ║ each m = one subset  ║
║ Check if element i is in set ║ mask & (1<<i)      ║ bit i = membership    ║
║ Add element i to set         ║ mask | (1<<i)      ║ set bit i             ║
║ Remove element i from set    ║ mask & ~(1<<i)     ║ clear bit i           ║
║ Swap without temp            ║ a^=b; b^=a; a^=b  ║ XOR swap              ║
║ Is odd?                      ║ n & 1              ║ last bit check        ║
╚══════════════════════════════╩══════════════════╩═══════════════════════╝
```

---

### 🧠 Memory Tricks

> **XOR = "Same cancels, different survives."** Used for finding unique elements.
>
> **n & (n-1) = "Kill the lowest set bit."** Used for counting bits and power-of-2 check.
>
> **Bitmask = "Integer as a set."** Bit i = element i's membership. `|` = union, `&` = intersection, `^` = symmetric difference.

### Practice Problems

| # | Problem | Difficulty | Pattern |
|---|---|---|---|
| LC 136 | Single Number | 🟢 | XOR |
| LC 191 | Number of 1 Bits | 🟢 | Kernighan's |
| LC 338 | Counting Bits | 🟢 | DP + bit shift |
| LC 231 | Power of Two | 🟢 | n & (n-1) |
| LC 78 | Subsets (bitmask) | 🟡 | enumerate 2ⁿ |
| LC 1125 | Smallest Sufficient Team | 🔴 | bitmask DP |
| LC 1595 | Min Cost to Connect Groups | 🔴 | bitmask DP |
| LC 943 | Shortest Superstring | 🔴 | TSP bitmask DP |
| LC 847 | Shortest Path Visiting All | 🔴 | BFS + bitmask |

---

### When to Use Bitmask DP

| Signal | Example |
|---|---|
| n ≤ 20 elements | "Assign n people to n tasks optimally" |
| "Visit all" / "use each exactly once" | TSP, assignment problems |
| Track a SUBSET of items | "Which skills have been covered?" |
| Exponential but n is small | 2²⁰ ≈ 1M states — feasible |
