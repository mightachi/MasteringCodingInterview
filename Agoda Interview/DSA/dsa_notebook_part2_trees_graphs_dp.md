# 🧠 DSA Interview Prep — Complete Explained Notebook (Part 2/3)
## Trees, Graphs & Dynamic Programming

---

# 3. TREES

---

## 3.1 Tree BFS (Level-Order Traversal)

### Mental Model

> **BFS = Queue.** Process one level at a time. Snapshot the queue size at each level, process exactly that many nodes, then all children form the next level.

**When BFS?** Level-by-level info, shortest path in unweighted tree, "rightmost at each level."

---

### Template 1: Level Order Traversal

```python
from collections import deque

def level_order(root):
    if not root: return []
    res = []; q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):          # WHY snapshot len? process EXACTLY this level's nodes
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)    # WHY check None? avoid pushing null nodes
            if node.right: q.append(node.right)
        res.append(level)
    return res
```

**WHY `range(len(q))` instead of `while q`?** We need to separate levels. At the start of each outer loop, `len(q)` = number of nodes at the **current** level. Processing exactly that many ensures children (next level) aren't mixed in.

```
Tree:     3
        /   \
       9    20
           /  \
          15   7

Queue progression:
  Level 0: q=[3]        → process 1 node  → level=[3]
  Level 1: q=[9,20]     → process 2 nodes → level=[9,20]
  Level 2: q=[15,7]     → process 2 nodes → level=[15,7]
  
Result: [[3],[9,20],[15,7]] ✅
```

---

### Template 2: Right Side View

```python
def right_side_view_v2(root):
    res = []; q = deque([root]) if root else deque()
    while q:
        for _ in range(len(q) - 1):       # WHY len-1? process all EXCEPT the last
            n = q.popleft()
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        last = q.popleft()                 # WHY separate? this is the RIGHTMOST at this level
        res.append(last.val)
        if last.left: q.append(last.left)
        if last.right: q.append(last.right)
    return res
```

**WHY the last one is special?** "Right side view" = the last node at each level when viewed from the right. We process all-but-last normally, then handle the last separately to record its value.

---

## 3.2 Tree DFS & Recursion

### Mental Model

> For each DFS problem, ask: **"What should each recursive call RETURN to its parent?"** This defines your recurrence.

| Problem | Returns | Tracks globally |
|---|---|---|
| Max Depth | height of subtree | — |
| Diameter | height of subtree | max(L+R) through each node |
| Max Path Sum | best single-branch sum | max(node+L+R) path through each node |
| LCA | found node (or None) | — |

---

### Template 1: Max Depth

```python
def max_depth(root):
    if not root: return 0                    # WHY? empty tree has depth 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
    # WHY 1+max? current node (1) plus the deeper subtree
```

---

### Template 2: Diameter of Binary Tree

```python
def diameter_of_binary_tree(root):
    best = [0]                              # WHY list? mutable container for closure variable
    def height(node):
        if not node: return 0
        L = height(node.left)
        R = height(node.right)
        best[0] = max(best[0], L + R)       # WHY L+R? path through this node = left height + right height
        return 1 + max(L, R)                # WHY return max? parent needs single-branch height
    height(root)
    return best[0]
```

**WHY `best[0]` (list) instead of `best` (int)?** In Python, nested functions can read outer variables but can't rebind them (without `nonlocal`). Using a list is a workaround — we mutate `best[0]`, not rebind `best`.

**WHY does height return `1 + max(L,R)` but track `L+R`?**
- **Return:** The parent needs the **longest single branch** going down through this node.
- **Track:** The **diameter** is the longest path, which can bend through this node using **both** branches.

```
        1
       / \
      2   3     height(2)=2, height(3)=1
     / \        diameter at node 1 = 2+1 = 3 (path: 4-2-1-3)
    4   5       return to parent: 1+max(2,1) = 3
```

---

### Template 3: Lowest Common Ancestor (LCA)

```python
def lowest_common_ancestor(root, p, q):
    if not root or root == p or root == q: return root  # WHY? found target or hit null
    left  = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    return root if left and right else (left or right)
    # WHY? if found on BOTH sides → this node is LCA
    # if found on ONE side → propagate that result upward
```

**WHY this works:**
```
Case 1: p in left subtree, q in right subtree
  → left = p (or some node), right = q (or some node)
  → both non-None → current node IS the LCA ✅

Case 2: Both p and q in left subtree
  → right = None, left = LCA of p,q (found deeper)
  → return left (propagate up) ✅

Case 3: Current node IS p or q
  → return immediately, the other target must be below OR elsewhere
```

---

### Template 4: Max Path Sum

```python
def max_path_sum(root):
    best = [float('-inf')]
    def dfs(node):
        if not node: return 0
        L = max(dfs(node.left), 0)    # WHY max(.,0)? ignore negative branches (don't help)
        R = max(dfs(node.right), 0)
        best[0] = max(best[0], node.val + L + R)  # WHY L+R? path bending through this node
        return node.val + max(L, R)                # WHY max? parent can only use ONE branch
    dfs(root)
    return best[0]
```

**WHY `max(dfs(...), 0)`?** If a subtree's best path sum is negative, we're better off not including it at all (take 0 instead). A negative branch only hurts the total.

**WHY return `max(L,R)` not `L+R`?** A path can't fork. When passing upward to the parent, we can only extend through ONE child. The path through the node bends only once.

```
       -10
       / \
      9  20      Path bending at 20: 15+20+7 = 42
        / \      But 20 returns to -10: 20+max(15,7) = 35 (can't fork)
       15  7     
```

---

## 3.3 BST Operations

### Template 1: Validate BST

```python
def is_valid_bst(root, lo=float('-inf'), hi=float('inf')):
    if not root: return True
    if not (lo < root.val < hi): return False    # WHY strict <? BST requires strictly less/greater
    return (is_valid_bst(root.left, lo, root.val) and  # WHY root.val as hi? left must be < current
            is_valid_bst(root.right, root.val, hi))    # WHY root.val as lo? right must be > current
```

**WHY pass bounds (not just compare with parent)?** A node must be valid against ALL ancestors, not just its parent:
```
      5
     / \
    1   6
       / \
      3   7    ← 3 is valid parent (6), BUT invalid: 3 < 5 (root). Must check bounds!
```

---

### Template 2: Kth Smallest (Iterative Inorder)

```python
def kth_smallest(root, k):
    stack = []; node = root
    while stack or node:
        while node: stack.append(node); node = node.left  # WHY? go as left as possible
        node = stack.pop()                                 # WHY? leftmost unvisited = next smallest
        k -= 1
        if k == 0: return node.val                         # WHY? kth pop = kth smallest
        node = node.right                                  # WHY? explore right subtree next
```

**WHY inorder = sorted order?** BST property: left < root < right. Inorder visits left, root, right → ascending order.

---

### Template 3: LCA of BST (Optimized with BST Property)

```python
def lca_bst(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val: root = root.left    # WHY? both smaller → LCA must be left
        elif p.val > root.val and q.val > root.val: root = root.right # WHY? both larger → LCA must be right
        else: return root                                              # WHY? split point = LCA
```

**WHY O(h) instead of O(n)?** BST property lets us skip half the tree at each step. No need to check both subtrees.

---

### Template 4: Sorted Array to BST

```python
def sorted_array_to_bst(nums):
    if not nums: return None
    mid = len(nums) // 2                    # WHY mid? balanced tree needs equal halves
    node = TreeNode(nums[mid])
    node.left  = sorted_array_to_bst(nums[:mid])     # WHY [:mid]? everything smaller → left
    node.right = sorted_array_to_bst(nums[mid+1:])   # WHY [mid+1:]? everything larger → right
    return node
```

**WHY always pick middle?** Creates a **balanced** BST with O(log n) height. If we picked the first element, we'd get a skewed tree (linked list).

---

# 4. GRAPHS

---

## 4.1 Graph BFS & DFS

### Template 1: Number of Islands (Grid BFS)

```python
def num_islands_bfs(grid):
    if not grid: return 0
    nr, nc = len(grid), len(grid[0])
    count = 0
    def bfs(r, c):
        q = deque([(r,c)]); grid[r][c] = '0'       # WHY mark '0' immediately? prevent re-visiting
        while q:
            r,c = q.popleft()
            for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:  # WHY 4 directions? grid adjacency
                nr2,nc2 = r+dr, c+dc
                if 0<=nr2<nr and 0<=nc2<nc and grid[nr2][nc2]=='1':
                    grid[nr2][nc2]='0'; q.append((nr2,nc2))  # WHY mark BEFORE enqueue? avoids duplicates
    for r in range(nr):
        for c in range(nc):
            if grid[r][c]=='1': count+=1; bfs(r,c)  # WHY? each BFS explores one complete island
    return count
```

**WHY mark visited BEFORE enqueuing (not after dequeuing)?** Multiple cells can enqueue the same neighbor before it's dequeued → duplicates. Marking on enqueue prevents this.

---

### Template 2: Rotting Oranges (Multi-Source BFS)

```python
def oranges_rotting(grid):
    nr, nc = len(grid), len(grid[0])
    q = deque(); fresh = 0
    for r in range(nr):
        for c in range(nc):
            if grid[r][c]==2: q.append((r,c,0))     # WHY all rotten sources? they rot SIMULTANEOUSLY
            elif grid[r][c]==1: fresh+=1
    minutes = 0
    while q:
        r,c,t = q.popleft()
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr2,nc2 = r+dr,c+dc
            if 0<=nr2<nr and 0<=nc2<nc and grid[nr2][nc2]==1:
                grid[nr2][nc2]=2; fresh-=1
                minutes=t+1; q.append((nr2,nc2,t+1))  # WHY t+1? next minute
    return minutes if fresh==0 else -1                  # WHY -1? unreachable fresh oranges
```

**WHY "multi-source"?** All rotten oranges start spreading simultaneously. Enqueue ALL rotten positions at time 0 → BFS naturally handles simultaneous spread level by level.

---

## 4.2 Topological Sort (Kahn's Algorithm)

```python
def topo_sort_kahn(n, prerequisites):
    graph = defaultdict(list)
    in_degree = [0] * n
    for a, b in prerequisites:           # b → a (b must come before a)
        graph[b].append(a)
        in_degree[a] += 1
    q = deque(i for i in range(n) if in_degree[i] == 0)  # WHY? nodes with no prereqs can go first
    order = []
    while q:
        node = q.popleft(); order.append(node)
        for nb in graph[node]:
            in_degree[nb] -= 1                    # WHY? one prereq satisfied
            if in_degree[nb] == 0: q.append(nb)   # WHY? all prereqs done → ready to process
    return order if len(order) == n else []         # WHY? if not all nodes → CYCLE exists
```

**WHY start with in-degree 0?** These nodes have no prerequisites — they're free to go first. Processing them reduces in-degrees of their neighbors, potentially freeing more nodes.

**WHY check `len(order) == n`?** In a cycle, some nodes always have in-degree > 0 (circular dependency). They never enter the queue → order is incomplete → cycle detected.

**🧠 Memorize:** "Start with the free nodes (in-degree 0). Process → reduce neighbors → newly free nodes → repeat."

---

## 4.3 Dijkstra's Algorithm

```python
import heapq

def dijkstra(n, edges, source):
    graph = defaultdict(list)
    for u, v, w in edges: graph[u].append((v, w))
    dist = [float('inf')] * (n + 1)
    dist[source] = 0
    heap = [(0, source)]                    # WHY heap? always process nearest unvisited node (greedy)
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]: continue             # WHY? stale entry — we already found a shorter path
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:        # WHY? found a shorter route to v
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))  # WHY push not decrease-key? simpler, stale check handles it
    return dist[1:]
```

**WHY `if d > dist[u]: continue`?** We may push the same node multiple times with different distances. When we pop a node, if its recorded distance is already shorter than what we popped, this entry is stale → skip.

**WHY min-heap (not BFS)?** BFS works for unweighted. With weights, we must process nodes in order of shortest known distance. The heap gives us the nearest unvisited node in O(log n).

**🧠 Memorize:** "Greedy: always expand the nearest. Heap gives nearest. Skip stale. Relax neighbors."

---

## 4.4 Union-Find

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))     # WHY self-parent? each node starts as its own root
        self.rank   = [0] * n
        self.count  = n                  # number of components

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # WHY path compression? flattens tree → near O(1)
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py: return False         # WHY False? already connected → this edge creates a CYCLE
        if self.rank[px] < self.rank[py]: px, py = py, px  # WHY? attach shorter tree under taller
        self.parent[py] = px
        if self.rank[px] == self.rank[py]: self.rank[px] += 1  # WHY? equal rank → combined tree is taller
        self.count -= 1
        return True
```

**WHY path compression?** Without it, `find` can be O(n) on a skewed tree. With path compression, subsequent finds are O(1) — every node points directly to root.

**WHY union by rank?** Prevents the tree from becoming a linked list. Always attach the shorter tree under the taller one → tree stays balanced.

**Combined: O(α(n)) ≈ O(1)** per operation (inverse Ackermann function — practically constant).

---

# 5. DYNAMIC PROGRAMMING

---

### The 5-Step DP Framework

```
1. DEFINE STATE:   What does dp[i] represent?
2. RECURRENCE:     How does dp[i] relate to smaller states?
3. BASE CASE:      What are dp[0], dp[1], etc.?
4. FILL ORDER:     Left→right? Bottom→up? Top-down with memo?
5. OPTIMIZE SPACE: Can 2D → 1D? Can array → two variables?
```

---

## 5.1 1D DP

### Template 1: Climbing Stairs

```python
def climb_stairs(n):
    if n <= 2: return n
    a, b = 1, 2                    # WHY? dp[1]=1, dp[2]=2
    for _ in range(3, n+1):
        a, b = b, a+b             # WHY a+b? ways(n) = ways(n-1) + ways(n-2) — Fibonacci!
    return b
```

**WHY Fibonacci?** From step `n`, you could have come from step `n-1` (one jump) or `n-2` (two jump). Total ways = sum of both.

---

### Template 2: House Robber

```python
def house_robber(nums):
    prev2 = prev1 = 0                  # WHY 0? robbing no houses = 0 profit
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
        # WHY? at each house: skip (prev1) vs rob (prev2 + current)
        # Can't rob adjacent → if rob current, use prev2 (skipped last)
    return prev1
```

**State transition:**
```
dp[i] = max(dp[i-1], dp[i-2] + nums[i])
         ↑ skip      ↑ rob current (must have skipped previous)
         
Space optimized: only need dp[i-1] and dp[i-2] → two variables.
```

### House Robber II (Circular)

```python
def house_robber_ii(nums):
    def rob(arr):                       # same as house_robber
        prev2 = prev1 = 0
        for x in arr: prev2, prev1 = prev1, max(prev1, prev2+x)
        return prev1
    n = len(nums)
    if n == 1: return nums[0]
    return max(rob(nums[:-1]), rob(nums[1:]))  # WHY two calls? can't rob BOTH first and last (circular)
```

**WHY `max(rob(0..n-2), rob(1..n-1))`?** In a circle, house 0 and house n-1 are adjacent. We can't rob both. So solve two sub-problems: without last house, without first house.

---

### Template 3: Word Break

```python
def word_break(s, word_dict):
    n = len(s); word_set = set(word_dict)  # WHY set? O(1) lookup vs O(n) in list
    dp = [False] * (n+1); dp[0] = True     # WHY dp[0]=True? empty string is "breakable"
    for i in range(1, n+1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:   # WHY? if s[0..j-1] is breakable AND s[j..i-1] is a word
                dp[i] = True; break             # WHY break? one valid split is enough
    return dp[n]
```

**`dp[i]` = "Can `s[0..i-1]` be segmented into dictionary words?"**

```
s = "leetcode", dict = {"leet", "code"}

dp[0]=T (empty)
dp[4]: j=0, dp[0]=T and s[0:4]="leet" in dict → dp[4]=True
dp[8]: j=4, dp[4]=T and s[4:8]="code" in dict → dp[8]=True ✅
```

---

### Template 4: Longest Increasing Subsequence (O(n log n))

```python
from bisect import bisect_left
def length_of_LIS(nums):
    tails = []                          # tails[i] = smallest tail of all increasing subsequences of length i+1
    for x in nums:
        pos = bisect_left(tails, x)    # WHY bisect? find where x fits in the sorted tails array
        if pos == len(tails): tails.append(x)  # WHY? x extends the longest subsequence
        else:                 tails[pos] = x   # WHY? x can replace to give a SMALLER tail (better for future)
    return len(tails)
```

**WHY is `tails` always sorted?** We only append values larger than the last element, and replacements maintain sorted order (replacing a larger value with a smaller one).

**WHY does `len(tails)` give the LIS length?** Each index in `tails` represents "the best possible tail for a subsequence of this length." The array's length = longest subsequence we've found.

```
nums = [10, 9, 2, 5, 3, 7, 101, 18]

tails progression:
  10  → [10]
  9   → [9]       (replace 10 with 9 — smaller tail for length-1)
  2   → [2]       (replace 9 with 2)
  5   → [2, 5]    (extends)
  3   → [2, 3]    (replace 5 with 3)
  7   → [2, 3, 7] (extends)
  101 → [2, 3, 7, 101] (extends) → length 4 ✅
  18  → [2, 3, 7, 18]  (replace 101)
```

---

## 5.2 2D DP & Subsequences

### Template 1: Longest Common Subsequence

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0]*(n+1) for _ in range(m+1)]      # WHY (m+1)×(n+1)? row 0 and col 0 = empty string base
    for i in range(1, m+1):
        for j in range(1, n+1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1   # WHY +1? matching char extends the LCS
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # WHY max? skip char from either string
    return dp[m][n]
```

**`dp[i][j]` = LCS length of `text1[0..i-1]` and `text2[0..j-1]`.**

```
text1 = "abcde", text2 = "ace"

       ""  a  c  e
  ""  [ 0  0  0  0 ]
   a  [ 0  1  1  1 ]    a==a → dp[0][0]+1=1
   b  [ 0  1  1  1 ]    b≠a,c,e → max of above/left
   c  [ 0  1  2  2 ]    c==c → dp[1][1]+1=2
   d  [ 0  1  2  2 ]
   e  [ 0  1  2  3 ]    e==e → dp[3][2]+1=3 ✅
```

---

### Template 2: Edit Distance

```python
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i      # WHY? deleting i chars from word1 to match ""
    for j in range(n+1): dp[0][j] = j      # WHY? inserting j chars to build word2 from ""
    for i in range(1, m+1):
        for j in range(1, n+1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]    # WHY? chars match → no edit needed, inherit diagonal
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],             # DELETE from word1
                    dp[i][j-1],             # INSERT into word1
                    dp[i-1][j-1]            # REPLACE in word1
                )
    return dp[m][n]
```

**🧠 Memorize the 3 operations:**
```
         dp[i-1][j-1]  dp[i-1][j]
              ↘ replace   ↓ delete
         dp[i][j-1] → dp[i][j]
              insert
```

---

### Template 3: Maximal Square

```python
def maximal_square(matrix):
    if not matrix: return 0
    nr, nc = len(matrix), len(matrix[0])
    dp = [[0]*nc for _ in range(nr)]; best = 0
    for i in range(nr):
        for j in range(nc):
            if matrix[i][j] == '1':
                dp[i][j] = (1 if i==0 or j==0 else
                            min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1)
                # WHY min of 3 neighbors? the square is limited by its WEAKEST corner
                best = max(best, dp[i][j])
    return best * best                     # WHY squared? dp stores side length, answer needs area
```

**WHY `min(top, left, diagonal) + 1`?** The largest square with bottom-right at (i,j) is constrained by the smallest square that its three neighbors can form. If any neighbor has a smaller square, the current one can't be bigger.

---

## 5.3 Knapsack Patterns

### Template 1: 0/1 Knapsack — Partition Equal Subset Sum

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2: return False             # WHY? odd total can't be split equally
    target = total // 2
    dp = {0}                               # WHY set? track reachable sums efficiently
    for x in nums:
        dp |= {s + x for s in dp}         # WHY |=? add all new sums reachable by including x
    return target in dp
```

**WHY is this 0/1 knapsack?** Each number is used at most once. Can we find a subset summing to `total/2`?

---

### Template 2: Coin Change 2 — Count Ways (Unbounded)

```python
def coin_change_2(amount, coins):
    dp = [0] * (amount + 1); dp[0] = 1    # WHY dp[0]=1? one way to make amount 0 (take nothing)
    for coin in coins:                      # WHY outer=coins? ensures each combination counted once
        for a in range(coin, amount+1):     # WHY inner=amounts? allows reuse of same coin
            dp[a] += dp[a-coin]
    return dp[amount]
```

**WHY `coins` in outer loop?** If amounts were outer, we'd count different ORDERINGS (permutations). Coins-outer counts COMBINATIONS (order doesn't matter).

```
Coins outer: process coin=1 fully, then coin=2, then coin=5
  [1,1,2] counted once (coin 1 processed before coin 2)
  [2,1,1] is the SAME combination → NOT counted again ✅

Amounts outer: at each amount, try all coins
  [1,1,2] and [2,1,1] would both be counted ❌
```

---

### Template 3: Target Sum

```python
def find_target_sum_ways(nums, target):
    total = sum(nums)
    if (total + target) % 2 or abs(target) > total: return 0  # WHY? math constraint
    cap = (total + target) // 2           # WHY? P-N=target, P+N=total → P=(total+target)/2
    dp = [0] * (cap + 1); dp[0] = 1
    for x in nums:
        for j in range(cap, x-1, -1):    # WHY reverse? 0/1 knapsack — each num used once
            dp[j] += dp[j-x]
    return dp[cap]
```

**WHY reverse iteration?** If we iterate forward, `dp[j]` might use the CURRENT element multiple times (unbounded). Reverse ensures each element is used at most once.

**WHY the math transformation?** Split nums into P (positive) and N (negative): `P - N = target`, `P + N = total`. Solving: `P = (total + target)/2`. Now it's a standard subset sum problem.

---

> **Continued in Part 3: Trie, Heap, Linked List, Matrix, Line Sweep, Hashing, and Cheat Sheets.**
