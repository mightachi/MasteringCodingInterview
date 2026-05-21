# 🧠 DSA Interview Prep — Complete Explained Notebook (Part 1/3)
## Arrays, Stacks & Queues — Every Template With WHY

> [!IMPORTANT]
> **How to use:** Each template has ① Mental Model ② Code with inline WHY ③ Key Dry Run ④ Memory Trick ⑤ Common Mistakes. Read **Mental Model first**, then trace the code.

---

# 1. ARRAYS

---

## 1.1 Two Pointers

### Mental Model

Two indices moving through data in coordinated fashion. **Eliminates nested loops** by encoding both search positions in two pointers.

| Variant | When | Movement |
|---|---|---|
| **Opposite-end** | Sorted + pair condition | Converge inward |
| **Same-direction** | Partition in-place, cycle | Fast outpaces slow |
| **Multi-pointer** | Triplets, 3-way partition | Fix one + two-pointer |

---

### Template 1: Opposite Ends — Two Sum Sorted

```python
def two_sum_sorted(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:                      # WHY <? pairs need distinct indices
        s = nums[lo] + nums[hi]
        if s == target:   return [lo, hi]
        elif s < target:  lo += 1       # WHY? sum too small → need larger (move left up)
        else:             hi -= 1       # WHY? sum too big → need smaller (move right down)
    return []
```

**WHY it works:** Array is sorted. If sum is too small, moving `lo` right is the ONLY way to increase it (hi is already the largest remaining). If sum is too big, moving `hi` left is the ONLY way to decrease it. We never skip a valid pair.

**Dry Run:** `[2, 7, 11, 15]`, target=9
```
lo=0, hi=3: 2+15=17 > 9 → hi=2
lo=0, hi=2: 2+11=13 > 9 → hi=1
lo=0, hi=1: 2+7=9 == 9 → return [0,1] ✅
```

---

### Template 2: 3Sum

```python
def three_sum(nums):
    nums.sort()                                     # WHY? enables two-pointer + duplicate skipping
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]: continue  # WHY? skip duplicate "i" to avoid duplicate triplets
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s == 0:
                res.append([nums[i], nums[lo], nums[hi]])
                while lo < hi and nums[lo] == nums[lo+1]: lo += 1  # WHY? skip duplicate lo
                while lo < hi and nums[hi] == nums[hi-1]: hi -= 1  # WHY? skip duplicate hi
                lo += 1; hi -= 1                    # WHY both? current pair is consumed
            elif s < 0: lo += 1                     # WHY? need larger sum
            else:       hi -= 1                     # WHY? need smaller sum
    return res
```

**WHY fix one + two-pointer?** 3Sum = fix `nums[i]`, then solve 2Sum for `target = -nums[i]` on `nums[i+1:]`. Reduces O(n³) brute force to O(n²).

**WHY `i > 0` in duplicate check (not `i > -1` or `i >= 0`)?** Index 0 is always valid (first element). Only skip when we've ALREADY processed this same value.

**🧠 Memorize:** "Sort → Fix one → Two-pointer the rest → Skip duplicates at all 3 levels"

---

### Template 3: Container With Most Water

```python
def max_water(height):
    lo, hi = 0, len(height) - 1
    best = 0
    while lo < hi:
        best = max(best, min(height[lo], height[hi]) * (hi - lo))
        if height[lo] < height[hi]: lo += 1   # WHY? move the SHORTER side
        else:                        hi -= 1
    return best
```

**WHY move the shorter side?** Moving the taller side can NEVER increase the area (water level is bounded by the shorter side, and width decreases). Moving the shorter side MIGHT find a taller bar → potentially more area. This greedy choice is provably optimal.

```
height[lo]=1    height[hi]=8
   ┌─┐               ┌─┐
   │ │               │ │   Water bounded by shorter (1)
   │1│ ≈ ≈ ≈ ≈ ≈ ≈ ≈ │8│   Moving 8 inward: still bounded by 1, but width decreases → worse
   └─┘               └─┘   Moving 1 inward: might find height 5 → area increases!
```

---

### Template 4: Dutch National Flag (Sort Colors)

```python
def sort_colors(nums):
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:                          # WHY <=? mid==hi is still unprocessed
        if   nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1; mid += 1                 # WHY both? swapped element from lo is ≤1 (already seen)
        elif nums[mid] == 1:
            mid += 1                          # WHY? 1 is in the right place
        else:  # nums[mid] == 2
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1                           # WHY no mid++? swapped element is UNKNOWN (from hi)
```

**WHY no `mid++` on swap with `hi`?** The element swapped from `hi` hasn't been examined yet — could be 0, 1, or 2. Must check it next iteration.

**🧠 Memorize:** "0→swap with lo (both advance), 1→mid advances, 2→swap with hi (only hi retreats)"

---

### Two Pointers Common Mistakes

| Mistake | Fix |
|---|---|
| Not sorting before 3Sum | `nums.sort()` first |
| `while lo <= hi` for pairs | Use `<` (pairs need distinct indices) |
| Moving wrong pointer in Container | Always move the **shorter** side |
| Incrementing `mid` after swap with `hi` | DON'T — swapped element is unexamined |
| Not skipping duplicates in 3Sum | Skip at all 3 levels: i, lo, hi |

---

## 1.2 Sliding Window

### Mental Model

Maintain a window `[lo, hi]` over contiguous elements. Avoid re-computation by **adding one element and removing one** instead of re-scanning.

| Type | Strategy | Use For |
|---|---|---|
| **Fixed** | Both pointers move together | "Every subarray of size K" |
| **Variable (longest)** | Shrink on **violation** | "Longest substring with property X" |
| **Variable (shortest)** | Shrink on **satisfaction** | "Shortest subarray satisfying Y" |
| **Anagram/Permutation** | Fixed size + frequency map | "Contains permutation of P" |

> [!IMPORTANT]
> **Longest vs Shortest — The Critical Difference:**
> - **Longest**: Shrink left when condition is **violated**. Record answer **after** shrinking.
> - **Shortest**: Shrink left when condition is **satisfied**. Record answer **while** shrinking.

---

### Template 1: Longest Substring Without Repeating (Variable, Longest)

```python
def length_of_longest_substring(s):
    seen = {}          # WHY dict? maps char → last seen index for O(1) jump
    lo = best = 0
    for hi, c in enumerate(s):
        if c in seen and seen[c] >= lo:   # WHY >= lo? only care about chars IN current window
            lo = seen[c] + 1              # WHY +1? jump PAST the duplicate
        seen[c] = hi
        best = max(best, hi - lo + 1)
    return best
```

**WHY `seen[c] >= lo`?** Character might exist in `seen` from a previous window that we've already moved past. Only react if the duplicate is within our current window `[lo, hi]`.

**Dry Run:** `"abcabcbb"`
```
hi=0 'a': seen={a:0}, lo=0, best=1  (window: "a")
hi=1 'b': seen={a:0,b:1}, best=2    (window: "ab")
hi=2 'c': seen={..c:2}, best=3      (window: "abc")
hi=3 'a': 'a' seen at 0, 0≥0 → lo=1. best=3  (window: "bca")
hi=4 'b': 'b' seen at 1, 1≥1 → lo=2. best=3  (window: "cab")
...
Answer: 3 ✅
```

---

### Template 2: Minimum Size Subarray Sum (Variable, Shortest)

```python
def min_subarray_len(target, nums):
    lo = window_sum = 0
    best = float('inf')
    for hi in range(len(nums)):
        window_sum += nums[hi]              # EXPAND: add right element
        while window_sum >= target:         # WHY while? shrink as much as possible
            best = min(best, hi - lo + 1)   # WHY record INSIDE while? shortest = most shrunk
            window_sum -= nums[lo]; lo += 1 # SHRINK: remove left element
    return best if best != float('inf') else 0
```

**WHY record inside the while loop (not outside)?** We want the SHORTEST valid window. The more we shrink, the shorter the window gets. Record at each shrink step.

**Dry Run:** `target=7, [2,3,1,2,4,3]`
```
hi=3: sum=8≥7 → best=4, remove 2→sum=6 < 7. stop.
hi=4: sum=10≥7 → best=4→3, remove 3→sum=7≥7 → best=3→2... 
...keeps shrinking until sum=6<7
Answer: 2 (subarray [4,3]) ✅
```

---

### Template 3: Shortest Subarray with Sum ≥ K (WITH negatives)

```python
from collections import deque

def shortest_subarray(nums, target):
    n = len(nums)
    prefix = [0] * (n + 1)                  # WHY prefix? with negatives, window sum isn't monotonic
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]

    dq = deque()          # WHY deque? monotonic queue of prefix indices
    best = float('inf')

    for j in range(n + 1):
        # WHY popleft? if prefix[j]-prefix[dq[0]] ≥ target, we found a valid subarray
        # and dq[0] is the SMALLEST index → shortest possible with this j
        while dq and prefix[j] - prefix[dq[0]] >= target:
            best = min(best, j - dq[0])
            dq.popleft()

        # WHY pop from back? if prefix[j] ≤ prefix[dq[-1]], then dq[-1] is USELESS:
        # for any future k, prefix[k]-prefix[j] ≥ prefix[k]-prefix[dq[-1]]
        # AND j is later → shorter subarray. So dq[-1] is dominated.
        while dq and prefix[j] <= prefix[dq[-1]]:
            dq.pop()

        dq.append(j)

    return best if best != float('inf') else -1
```

**WHY can't we use the simple sliding window?** With negative numbers, the window sum isn't monotonic — shrinking from the left might increase the sum (if we remove a negative number). So we need prefix sums + monotonic deque.

**WHY is a dominated prefix useless?** If prefix[j] ≤ prefix[k] and j > k, then for any future index, subtracting prefix[j] gives a result at least as large (valid) AND the distance is shorter. So k can never be the optimal left endpoint.

---

### Template 4: Sliding Window Maximum (Fixed + Monotonic Deque)

```python
from collections import deque
def sliding_window_max(nums, k):
    dq = deque()   # WHY deque? need O(1) removal from both ends
    res = []       # stores INDICES in decreasing value order
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x: dq.pop()  # WHY? smaller values can NEVER be max while x exists
        dq.append(i)
        if dq[0] == i - k: dq.popleft()           # WHY? front is outside window, evict
        if i >= k - 1: res.append(nums[dq[0]])     # WHY k-1? first full window at index k-1
    return res
```

**🧠 Memorize (Throne Room):** "New king enters → kicks out everyone weaker (pop back). Old king leaves only when window slides past them (popleft front)."

**Dry Run:** `[1,3,-1,-3,5,3,6,7], k=3`
```
i=0: dq=[0:1]
i=1: 1≤3→pop. dq=[1:3]
i=2: -1<3→stay. dq=[1:3,2:-1]. i≥2→res=[3]
i=3: -3<-1→stay. dq=[1:3,2:-1,3:-3]. i-k=0,dq[0]=1≠0. res=[3,3]
i=4: pop everything<5. dq=[4:5]. res=[3,3,5]
i=5: 3<5→stay. dq=[4:5,5:3]. res=[3,3,5,5]
i=6: pop all<6. dq=[6:6]. res=[3,3,5,5,6]
i=7: pop all<7. dq=[7:7]. res=[3,3,5,5,6,7] ✅
```

---

### Template 5: Permutation in String (Anagram Check)

```python
def check_inclusion(s1, s2):
    from collections import Counter
    need = Counter(s1)                             # WHY? target frequencies
    have = Counter()
    formed = 0; required = len(need)               # WHY formed? O(1) match check vs O(26) dict compare
    lo = 0
    for hi, c in enumerate(s2):
        have[c] += 1
        if c in need and have[c] == need[c]: formed += 1  # WHY ==? only count at exact threshold
        while formed == required:                          # WHY while? try to tighten
            if hi - lo + 1 == len(s1): return True         # WHY check size? extra chars inflate window
            have[s2[lo]] -= 1
            if s2[lo] in need and have[s2[lo]] < need[s2[lo]]: formed -= 1  # WHY <? dropped below need
            lo += 1
    return False
```

**🧠 Memorize (Bouncer):** "Guest list = `need`. Room = `have`. `formed` = how many guests are fully checked in. When all checked in and room size matches → anagram found."

---

### Sliding Window Common Mistakes

| Mistake | Fix |
|---|---|
| Re-computing window sum from scratch | Add new element, subtract leaving element |
| Missing `seen[c] >= lo` check | Always verify duplicate is IN current window |
| Recording answer outside shrink loop (for shortest) | Record INSIDE `while` for shortest |
| Not cleaning hashmap (`del` when count=0) | `len(freq)` stays inflated |
| Using simple window for negative numbers | Need prefix sum + monotonic deque |

---

## 1.3 Prefix Sum

### Mental Model

Pre-compute cumulative sums: `prefix[i] = sum(arr[0..i-1])`. Any range sum becomes O(1): `sum(l,r) = prefix[r+1] - prefix[l]`.

**The killer combo:** Prefix Sum + HashMap → "subarray sum = K" in O(n).

> **Key insight:** If `prefix[j] - prefix[i] = K`, then `sum(arr[i..j-1]) = K`. So we look for previous prefix sums that equal `current_prefix - K`.

---

### Template 1: Build Prefix Sum

```python
def build_prefix(arr):
    prefix = [0] * (len(arr) + 1)        # WHY +1? prefix[0]=0 = empty sum sentinel
    for i, v in enumerate(arr):
        prefix[i+1] = prefix[i] + v
    return prefix   # sum(l,r) = prefix[r+1] - prefix[l]
```

---

### Template 2: Subarray Sum = K (THE Most Important Prefix Pattern)

```python
def subarray_sum_k(nums, k):
    count = 0; prefix = 0
    freq = {0: 1}                        # WHY {0:1}? handles subarrays starting at index 0
    for x in nums:
        prefix += x
        count += freq.get(prefix - k, 0) # WHY? how many previous prefixes differ by exactly k?
        freq[prefix] = freq.get(prefix, 0) + 1
    return count
```

**WHY `{0: 1}`?** Without it:
```
nums = [3], k = 3
prefix = 3. prefix - k = 0. Is 0 in freq? Without {0:1} → NO → miss!
With {0:1} → YES → count = 1 ✅ (subarray [3] itself)
```

**Dry Run:** `[1,1,1], k=2`
```
freq={0:1}
x=1: prefix=1. count+=freq.get(-1,0)=0. freq={0:1,1:1}
x=1: prefix=2. count+=freq.get(0,0)=1.  freq={0:1,1:1,2:1}  count=1
x=1: prefix=3. count+=freq.get(1,0)=1.  freq={0:1,1:1,2:1,3:1}  count=2
Answer: 2 ✅ (subarrays [1,1] at positions 0-1 and 1-2)
```

---

### Template 3: Pivot Index

```python
def find_pivot_index(nums):
    total = sum(nums); left = 0
    for i, x in enumerate(nums):
        if left == total - left - x: return i   # WHY? right_sum = total - left - nums[i]
        left += x
    return -1
```

**WHY `total - left - x`?** `right_sum = total_sum - left_sum - nums[i]` (exclude the pivot element itself from both sides).

---

### Template 4: Product Except Self

```python
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    for i in range(1, n):                # LEFT pass: prefix product
        out[i] = out[i-1] * nums[i-1]   # out[i] = product of all LEFT of i
    right = 1
    for i in range(n-1, -1, -1):         # RIGHT pass: suffix product
        out[i] *= right                  # WHY *=? multiply existing left product by right product
        right *= nums[i]
    return out
```

**WHY two passes?** `result[i] = (product of left) × (product of right)`. First pass fills left products, second pass multiplies in right products. No division needed (handles zeros!).

```
nums:    [1,   2,   3,   4]
Left:    [1,   1,   2,   6]    (product of everything LEFT)
Right:   [24,  12,  4,   1]    (product of everything RIGHT)
Result:  [24,  12,  8,   6]    left × right ✅
```

---

### Template 5: 2D Prefix Sum

```python
def build_2d_prefix(matrix):
    nr, nc = len(matrix), len(matrix[0])
    pre = [[0]*(nc+1) for _ in range(nr+1)]
    for i in range(1, nr+1):
        for j in range(1, nc+1):
            pre[i][j] = (matrix[i-1][j-1] + pre[i-1][j]
                         + pre[i][j-1] - pre[i-1][j-1])  # WHY subtract? inclusion-exclusion
    return pre
    # Query (r1,c1)..(r2,c2): pre[r2+1][c2+1] - pre[r1][c2+1] - pre[r2+1][c1] + pre[r1][c1]
```

**WHY inclusion-exclusion?** Adding top and left overlaps counts the top-left corner twice → subtract it.

---

## 1.4 Sorting Patterns

### Template 1: Merge Intervals

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])               # WHY start? makes overlapping intervals adjacent
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:                    # WHY <=? touching intervals merge too
            merged[-1][1] = max(merged[-1][1], end)   # WHY max? inner interval shouldn't shrink result
        else:
            merged.append([start, end])
    return merged
```

**🧠 Memorize:** "Sort-Seed-Scan: **S**tretch if overlap, **S**tart-new if gap."

---

### Template 2: Non-Overlapping Intervals (Min Removals)

```python
def erase_overlap_intervals(intervals):
    intervals.sort(key=lambda x: x[1])      # WHY sort by END? earliest finisher → most room for future
    removed = 0; end = float('-inf')
    for s, e in intervals:
        if s >= end: end = e                 # WHY? no overlap → keep this interval
        else:        removed += 1            # WHY? overlaps → remove it (greedy: keep earlier finisher)
    return removed
```

**WHY sort by END, not START?** This is **Activity Selection** — keeping the earliest finisher always leaves maximum room for subsequent intervals. Proven optimal by exchange argument.

**🧠 Memorize:** "**E**rase = sort by **E**nd. Keep earliest finisher."

---

### Template 3: Largest Number

```python
def largest_number(nums):
    from functools import cmp_to_key
    def cmp(a, b):
        if a+b > b+a: return -1       # WHY? "a first" makes larger number → a comes first
        elif a+b < b+a: return 1
        return 0
    nums = [str(n) for n in nums]     # WHY strings? need concatenation comparison
    nums.sort(key=cmp_to_key(cmp))
    return '0' if nums[0]=='0' else ''.join(nums)  # WHY '0' check? [0,0,0] → "0" not "000"
```

**WHY concatenation comparison works:** `a+b` and `b+a` have the **same length** → string comparison = numeric comparison. It defines a valid total ordering.

**🧠 Memorize:** "Concat-Compare: should a go first? Check `a+b > b+a`."

---

## 1.5 Kadane's Algorithm & Variants

### Template 1: Classic Kadane — Max Subarray Sum

```python
def max_subarray(nums):
    cur = best = nums[0]          # WHY nums[0]? starting with 0 fails for all-negative arrays
    for x in nums[1:]:
        cur = max(x, cur + x)    # WHY? "extend previous subarray" vs "start fresh"
        best = max(best, cur)    # WHY? track global best across all positions
    return best
```

**The Decision at Each Element:**
```
If cur (running sum) is NEGATIVE → starting fresh is better (x alone)
If cur is POSITIVE → extending helps (adds to x)
max(x, cur + x) encodes exactly this logic.
```

---

### Template 2: Max Product Subarray

```python
def max_product(nums):
    max_p = min_p = best = nums[0]
    for x in nums[1:]:
        candidates = (x, max_p * x, min_p * x)  # WHY min_p? negative × negative = positive!
        max_p = max(candidates)
        min_p = min(candidates)                   # WHY track min? it could flip to max next step
        best = max(best, max_p)
    return best
```

**WHY track both max AND min?** A large negative min can become a large positive max when multiplied by another negative number. Example: `min=-6`, next element `x=-2` → `-6 × -2 = 12`.

---

### Template 3: Circular Max Subarray Sum

```python
def max_circular_subarray(nums):
    def kadane(arr):
        cur = best = arr[0]
        for x in arr[1:]: cur = max(x, cur + x); best = max(best, cur)
        return best
    max_sum = kadane(nums)              # Case 1: no wrapping
    total = sum(nums)
    inv = [-x for x in nums]
    min_circular = total + kadane(inv)  # Case 2: wrapping = total - min_subarray
    # WHY invert? kadane(inv) finds max of inverted = -min of original
    # total + (-min) = total - min = wrap-around sum
    return max(max_sum, min_circular) if min_circular != 0 else max_sum
    # WHY != 0? if min_circular=0, ALL elements are negative → wrap takes nothing (invalid)
```

**🧠 Memorize:** "Kadane twice: normal max vs (total - min). Edge case: all negative → skip wrap."

---

### Template 4: Subarray Sum Divisible by K

```python
def check_subarray_sum(nums, k):
    seen = {0: -1}; prefix = 0            # WHY {0:-1}? handles subarrays starting at index 0
    for i, x in enumerate(nums):
        prefix = (prefix + x) % k         # WHY mod? only remainder matters for divisibility
        if prefix in seen:
            if i - seen[prefix] >= 2: return True  # WHY ≥2? problem requires length ≥ 2
        else:
            seen[prefix] = i               # WHY else (first only)? earliest index → longest distance
    return False
```

**WHY same remainder = divisible?** If `prefix[j] % k == prefix[i] % k`, then `(prefix[j] - prefix[i]) % k == 0` → the subarray between them has sum divisible by k.

---

# 2. STACKS & QUEUES

---

## 2.1 Monotonic Stack

### Mental Model

> **"Stack = waiting room. New arrival pops everyone it dominates. Each popped element gets its answer."**

Every element is pushed exactly once and popped at most once → O(n) total.

---

### Template 1: Next Greater Element

```python
def next_greater_element(nums):
    n = len(nums)
    res = [-1] * n            # WHY -1? elements that never get popped have no NGE
    stack = []                # WHY indices? need to know WHERE to write the answer
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:  # WHY <? new element IS the answer for smaller ones
            res[stack.pop()] = nums[i]              # WHY nums[i]? it's the next GREATER for popped element
        stack.append(i)
    return res
```

**Dry Run:** `[2,1,2,4,3]`
```
i=0: push 0.         stack:[0:2]
i=1: 2<1? NO. push.  stack:[0:2,1:1]
i=2: 1<2→pop 1, res[1]=2. 2<2? NO. push.  stack:[0:2,2:2]  res:[-1,2,-1,-1,-1]
i=3: 2<4→pop 2, res[2]=4. 2<4→pop 0, res[0]=4. push.  stack:[3:4]  res:[4,2,4,-1,-1]
i=4: 4<3? NO. push.  stack:[3:4,4:3]
Result: [4,2,4,-1,-1] ✅
```

---

### Template 2: Daily Temperatures (Distance Instead of Value)

```python
def daily_temperatures(temps):
    res = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j       # WHY i-j? "how many DAYS until warmer" = index difference
        stack.append(i)
    return res
```

**🧠 Memorize:** "Same as NGE but write `i - j` (distance) instead of `nums[i]` (value)."

---

### Template 3: Largest Rectangle in Histogram

```python
def largest_rect_histogram(heights):
    heights = [0] + heights + [0]   # WHY sentinels? left prevents empty stack, right forces final flush
    stack = [0]; max_area = 0       # WHY [0]? start with left sentinel index
    for i in range(1, len(heights)):
        while heights[stack[-1]] > heights[i]:   # WHY >? shorter bar traps taller bars
            h = heights[stack.pop()]             # popped bar's height
            w = i - stack[-1] - 1                # WHY this formula? gap between LEFT boundary and RIGHT
            max_area = max(max_area, h * w)
        stack.append(i)
    return max_area
```

**WHY `w = i - stack[-1] - 1`?** After popping:
- `i` = right boundary (first shorter bar on the right)
- `stack[-1]` = new top = left boundary (first shorter bar on the left)
- Width = everything between boundaries (exclusive): `i - stack[-1] - 1`

```
stack[-1]    [popped bars]     i
   ↓        ← width →         ↓
  [1] [5] [6] [5] [3]       [2]
       ↑── h=5, w=3 ──↑
```

---

### Template 4: Trapping Rain Water

```python
def trap_water(height):
    stack = []; water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:      # WHY <? found a right wall taller than valley
            bottom = height[stack.pop()]            # valley floor
            if not stack: break                     # WHY? no left wall → water flows off
            left = stack[-1]                        # left wall (after pop)
            width = i - left - 1                    # horizontal span between walls
            bounded = min(h, height[left]) - bottom # WHY min? water limited by shorter wall
            water += bounded * width                # one horizontal layer of water
        stack.append(i)
    return water
```

**🧠 Memorize:** "Pop = valley **bottom**. Stack top after pop = **left wall**. Current bar = **right wall**. Water = `min(walls) - bottom × width`."

---

## 2.2 Stack Design & Parentheses

### Template 1: Min Stack — O(1) getMin

```python
class MinStack:
    def __init__(self):
        self.stack = []                    # each element: (value, running_min)
    def push(self, val):
        cur_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, cur_min))  # WHY tuple? snapshot the min at each level
    def pop(self):   self.stack.pop()      # WHY just pop? previous element has ITS OWN correct min
    def top(self):   return self.stack[-1][0]
    def getMin(self):return self.stack[-1][1]
```

**🧠 Memorize:** "Every element carries its own minimum like a backpack. Pop → previous backpack is automatically correct."

---

### Template 2: Valid Parentheses

```python
def is_valid_parens(s):
    match = {')':'(', ']':'[', '}':'{'}   # WHY dict? maps closer → expected opener
    stack = []
    for c in s:
        if c in '([{': stack.append(c)    # WHY push? opener = promise, stack remembers order
        elif not stack or stack[-1] != match[c]: return False  # WHY? empty=nothing to match, mismatch=wrong type
        else: stack.pop()                 # WHY pop? promise fulfilled, remove it
    return not stack                      # WHY? leftover = unclosed openers
```

---

### Template 3: Longest Valid Parentheses

```python
def longest_valid_parens(s):
    stack = [-1]          # WHY -1 sentinel? base for measuring length at index 0
    best = 0
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)               # WHY push index? need distances, not characters
        else:
            stack.pop()
            if not stack:
                stack.append(i)           # WHY? unmatched ')' becomes new fence/boundary
            else:
                best = max(best, i - stack[-1])  # WHY? valid length = distance from last fence
    return best
```

**WHY `-1` sentinel?** For `"()"`: after popping index 0, stack=[-1]. Length = `1 - (-1) = 2`. Without sentinel, stack would be empty → crash or wrong result.

**WHY push `i` when stack empties?** An unmatched `)` acts as a **fence** — it separates valid regions. Everything after it starts measuring from this new boundary.

---

### Template 4: Remove Adjacent Duplicates

```python
def remove_duplicates(s):
    stack = []
    for c in s:
        if stack and stack[-1] == c: stack.pop()  # WHY? same as top → they cancel 💥
        else:                        stack.append(c)
    return ''.join(stack)
```

**WHY stack handles chain reactions?** After canceling `bb`, the `a` underneath is now exposed. The next `a` sees it immediately → auto-chains. No re-scanning needed.

```
"abbaca" → push a → push b → b matches b → pop (cancel) → a matches a → pop (chain!) → push c → push a → "ca"
```

---

## 2.3 Queue & Deque

### Template 1: Queue Using Two Stacks

```python
class MyQueue:
    def __init__(self):
        self.in_stack = []          # WHY two stacks? reversal converts LIFO → FIFO
        self.out_stack = []
    def push(self, x): self.in_stack.append(x)
    def _transfer(self):
        if not self.out_stack:      # WHY only when empty? preserves existing FIFO order
            while self.in_stack: self.out_stack.append(self.in_stack.pop())
    def pop(self):   self._transfer(); return self.out_stack.pop()
    def peek(self):  self._transfer(); return self.out_stack[-1]
    def empty(self): return not self.in_stack and not self.out_stack
```

**WHY two stacks gives FIFO?** Pouring stack A into stack B reverses the order: `[1,2,3]` becomes `[3,2,1]`. Popping from B gives `1` first → FIFO!

**WHY only transfer when `out_stack` is empty?** If it's not empty, it already has elements in correct FIFO order. Transferring new elements on top would break the order.

**Amortised O(1):** Each element is pushed twice (into in, then into out) and popped twice → 4 operations total → O(1) amortised per operation.

---

### Template 2: Shortest Subarray with Sum ≥ K (Monotonic Deque on Prefix)

```python
def shortest_subarray_sum_k(nums, k):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n): prefix[i+1] = prefix[i] + nums[i]
    dq = deque()    # WHY monotonic deque? prefix sums aren't sorted (negatives exist)
    res = n + 1
    for i in range(n + 1):
        while dq and prefix[i] - prefix[dq[0]] >= k:  # WHY popleft? found valid, try shorter
            res = min(res, i - dq.popleft())
        while dq and prefix[dq[-1]] >= prefix[i]:      # WHY pop? dominated candidates (same logic as sliding window max)
            dq.pop()
        dq.append(i)
    return res if res <= n else -1
```

**WHY this is harder than Template 2 (min subarray len)?** Negative numbers mean shrinking the window from the left might INCREASE the sum. We can't use simple sliding window. Instead, use prefix sums and find pairs where `prefix[j] - prefix[i] ≥ k` with minimum `j - i`.

---

> **Continued in Part 2: Trees, Graphs, DP, and Part 3: Trie, Heap, Linked List, Matrix, and more.**
