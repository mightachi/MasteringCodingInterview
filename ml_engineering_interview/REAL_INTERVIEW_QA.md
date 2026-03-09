# Real Interview Questions – Grouped, Deduplicated, with Solutions

This document consolidates **real interview questions** from Google, Tata Digital, Zzazz, Adobe, Zalando, BalanceHero, Wipro, Expedia, EY, and others. Similar questions are merged into **unique items**, grouped into **logical sections**, and answered with **solutions, examples, and technical explanations**.

---

## How to Use This Doc

- **Sections** are ordered by topic (Coding → Databases → ML → LLM/GenAI → MLOps → Behavioral).
- Each **question** has an **elaborated answer**: from basic concept → step-by-step reasoning → justification → advanced points. **Code** is included with line-by-line explanation where relevant.
- **Source companies** are noted for context; focus on the concept, not the company.
- Use this for deep revision: read the full explanation to justify solutions and handle follow-up questions in interviews.

**Answer format:** Each question is answered in a consistent structure where applicable:
1. **What** – Definition or what the concept/solution is.
2. **Why** – Motivation or why we need it.
3. **How** – Approach, steps, or how it works.
4. **Challenges solved** – What problems it addresses.
5. **Pros and cons** – Advantages and disadvantages.
6. **Difference from alternatives** – How it compares to other approaches.
7. **Most common errors** – Typical pitfalls or mistakes.

*(Not every point applies to every question; N/A or "see above" is used when irrelevant.)*

---

## Table of Contents

1. [Coding & Algorithms](#1-coding-algorithms)
2. [Databases & APIs](#2-databases-apis)
3. [Async, Concurrency & Backend](#3-async-concurrency-backend)
4. [Kafka & Messaging](#4-kafka-messaging)
5. [Search & Storage (Elasticsearch, MongoDB)](#5-search-storage)
6. [ML Fundamentals & Statistics](#6-ml-fundamentals-statistics)
7. [Ensemble Methods & Tree Models](#7-ensemble-methods-tree-models)
8. [Clustering & Dimensionality Reduction](#8-clustering-dimensionality-reduction)
9. [Deep Learning & Transformers](#9-deep-learning-transformers)
10. [LLM, RAG & Gen AI](#10-llm-rag-gen-ai)
11. [MLOps, Production & Feature Store](#11-mlops-production-feature-store)
12. [PySpark & Large-Scale Data](#12-pyspark-large-scale-data)
13. [Software Engineering Fundamentals](#13-software-engineering-fundamentals)
14. [Behavioral & Process](#14-behavioral-process)

---

<a id="1-coding-algorithms"></a>
## 1. Coding & Algorithms

### Q1.1 Minimum number of strokes to paint a fence (horizontal/vertical strokes)

**Source:** Google (Codeforces 448C)

**Problem:** Given an array of fence heights (e.g. `[2,2,1,3,1]`), find the minimum number of horizontal or vertical strokes to paint the board. Each stroke paints one unit height horizontally or one column vertically.

**Structured answer:**
1. **What:** Minimum number of brush strokes (each stroke is either one full row at some height or one full column from bottom to top) to completely paint a fence whose columns have given heights.
2. **Why:** Models optimal use of two types of strokes; useful in scheduling or resource-minimization problems.
3. **How:** For each contiguous segment [lo..hi] with a "base" (already painted height): compute minimum remaining height m; either use m horizontal strokes for that layer and recurse on sub-segments that extend above it, or use (hi−lo+1) vertical strokes; return the minimum of the two.
4. **Challenges solved:** Combines greedy (paint minimum layer) with recursion (sub-problems above that layer) and comparison with the all-vertical strategy.
5. **Pros and cons:** Pros: Correct, handles any height array. Cons: Naive implementation O(n²); need segment tree for O(n log n).
6. **Difference from alternatives:** Versus "always vertical": saves strokes when horizontal bands are beneficial. Versus "always horizontal": compares with vertical when segment is narrow/tall.
7. **Most common errors:** Forgetting to extend sub-segments above base+m; off-by-one in lo/hi; not taking min(horizontal+recurse, vertical).

**Answer:** Use a recursive/greedy idea: for a contiguous segment, either paint the whole segment with horizontal strokes (one per “layer”) or paint each column vertically. Take the minimum.

**What `lo`, `hi`, and `base` mean:**

| Parameter | Meaning |
|-----------|--------|
| **`lo`** | **Left index** of the current segment (inclusive). First column we consider. |
| **`hi`** | **Right index** of the current segment (inclusive). Together with `lo`, this is the **range of columns** `[lo..hi]` we are solving for. |
| **`base`** | **Height already painted** in earlier steps. We pretend everything from the ground up to height `base` is done. We only care about **remaining** height: `heights[i] - base`. So `base` "moves the floor" up as we paint horizontal layers. |

**Example:** `heights = [2, 2, 1, 3, 1]`, first call `min_strokes(heights, 0, 4, 0)`: `lo=0`, `hi=4` = whole fence (5 columns). `base=0` = nothing painted; remaining heights = [2,2,1,3,1]. Min remaining = 1, so we use **1 horizontal stroke** for the bottom layer. After that, the "floor" is at 1; remaining = [1,1,0,2,0]. Columns 2 and 4 are done; we **recurse** on the runs that still have height (indices 0–1 and 3) with **`base = 1`** and the corresponding `lo`/`hi`. So: **`lo`/`hi`** = which columns we consider; **`base`** = height already painted (we only count strokes for the part *above* `base`).

**Solution (recursive):** For segment `[lo..hi]` with base (already painted up to `base`): (1) Find min height in segment, subtract base → `m`. (2) Option A: use `m` horizontal strokes for the whole segment, then recurse on sub-segments that extend above `base + m`. (3) Option B: use `hi - lo + 1` vertical strokes. Return `min(optionA, optionB)`.

```python
def min_strokes(heights: list[int], lo: int, hi: int, base: int = 0) -> int:
    if lo > hi:
        return 0
    m = min(heights[i] for i in range(lo, hi + 1)) - base
    if m <= 0:
        return 0
    # Option A: m horizontal strokes + recurse on "upper" sub-segments
    total = m
    i = lo
    while i <= hi:
        if heights[i] - base <= m:
            i += 1
            continue
        j = i
        while j <= hi and heights[j] - base > m:
            j += 1
        total += min_strokes(heights, i, j - 1, base + m)
        i = j
    vertical = hi - lo + 1
    return min(total, vertical)

# Example: [2,2,1,3,1] → 3
# Full O(n) min-query version uses segment tree: see companies/google/min_num_of_strokes.py
```

**Technical note:** Recurrence: either paint the minimum layer horizontally and recurse on segments above it, or paint each column vertically. A segment tree can give min over a range in O(log n) for better complexity.

**Elaboration (scratch to advanced):** (1) **Why only two options?** For any contiguous segment, the optimal strategy is either paint each column vertically (cost = number of columns) or paint the bottom layer horizontally (minimum height in segment) and then solve the remaining "upper" sub-segments recursively. (2) **Correctness:** Painting the minimum layer with horizontal strokes covers every column with the fewest strokes for that layer; the recurrence compares this "horizontal + recurse" cost to "all vertical" and takes the minimum. (3) **Complexity:** Naive O(n²) (each level scans O(n), up to O(n) levels); with a segment tree for range-min, O(n log n).

---

### Q1.2 Sort array by sorting a subsequence / maximum subarray (sorted subsequence)

**Source:** Google (variant)

**Problem:** Array sorts entirely when a specific subsequence is sorted. Find that subsequence / maximum unsorted subarray (shortest contiguous subarray that, if sorted, makes the entire array sorted).

**Answer:** Find the leftmost index where order breaks (first i where nums[i] < nums[i-1]) and the rightmost (last i where nums[i] > nums[i+1]). Then extend this range: any element to the left that is greater than the minimum inside the range must be included (otherwise the array won't be sorted); similarly any element to the right that is less than the maximum inside the range must be included. The result is the shortest unsorted contiguous subarray.

**Elaboration:** (1) **From scratch:** If the array is already sorted, return (0,0). Otherwise there is at least one "dip" (nums[i] < nums[i-1]) and one "rise" (nums[i] > nums[i+1]). The unsorted region must include all such violations. (2) **Why extend?** The initial [left, right] might not be enough: e.g. [1,3,2,4] — left=1, right=2, but min in [3,2] is 2 and max is 3; the 1 to the left is ≤2 so we don't extend left; 4 to the right is ≥3 so we don't extend right. In [2,6,4,8,10,9,15], the unsorted region 6..9 has min=4, max=10; we must extend left until no element to the left is >4, and right until no element to the right is <10. (3) **Correctness:** After extension, sorting the subarray fixes all inversions and leaves the rest of the array already in order relative to the sorted subarray.

```python
def shortest_unsorted_subarray(nums: list[int]) -> tuple[int, int]:
    n = len(nums)
    left = next((i for i in range(1, n) if nums[i] < nums[i-1]), n)
    if left == n:
        return (0, 0)
    right = next((i for i in range(n-2, -1, -1) if nums[i] > nums[i+1]), -1)
    lo, hi = min(nums[left:right+1]), max(nums[left:right+1])
    while left > 0 and nums[left-1] > lo:
        left -= 1
    while right < n-1 and nums[right+1] < hi:
        right += 1
    return (left, right)
```

---

### Q1.3 Merge two sorted arrays into one sorted array (with or without extra space)

**Source:** Tata Digital, Adobe

**Answer (with extra space):** Two pointers i, j on arr1 and arr2; at each step compare arr1[i] and arr2[j], put the smaller into the result and advance that pointer. O(n+m) time, O(n+m) space. Standard merge from merge-sort.

**Answer (without extra space – Gap method):** Treat both arrays as one contiguous sequence (arr1 then arr2). Use the "gap method" from shell sort: start with gap = ceil((n+m)/2), and compare-swap elements at indices i and i+gap (they can be in the same array or across arr1 and arr2). Then reduce gap (e.g. gap = ceil(gap/2)) until gap is 0. After the last pass with gap=1, the combined sequence is sorted, with the smallest n elements in arr1 and the rest in arr2. O((n+m) log(n+m)) time, O(1) space.

**Elaboration:** (1) **Why gap method works:** Like shell sort, each gap pass moves elements that are gap positions apart closer to their final order; when gap=1 we do a full comparison pass that completes the merge. (2) **Index mapping:** When j = i + gap crosses from arr1 into arr2, we compare arr1[i] with arr2[j-n]; swaps are done in place. (3) **Constraint:** We must end with "first n smallest in arr1, last m in arr2" — the problem specifies modifying arr1 and arr2 so arr1 gets the first n and arr2 the last m elements of the sorted combined list.

```python
import math

def merge_sorted_no_extra_space(arr1: list[int], arr2: list[int]) -> None:
    n, m = len(arr1), len(arr2)
    gap = math.ceil((n + m) / 2)
    while gap > 0:
        i = 0
        while i + gap < n + m:
            j = i + gap
            if i < n and j < n:
                if arr1[i] > arr1[j]:
                    arr1[i], arr1[j] = arr1[j], arr1[i]
            elif i < n and j >= n:
                j2 = j - n
                if arr1[i] > arr2[j2]:
                    arr1[i], arr2[j2] = arr2[j2], arr1[i]
            else:
                i2, j2 = i - n, j - n
                if arr2[i2] > arr2[j2]:
                    arr2[i2], arr2[j2] = arr2[j2], arr2[i2]
            i += 1
        gap = gap // 2 if gap > 1 else 0
# Example: a=[2,4,7,10], b=[2,3] → a=[2,2,3,4], b=[7,10]
```

---

### Q1.4 Minimum days to make m bouquets (k adjacent flowers each)

**Source:** Zzazz (LeetCode 1482)

**Structured answer:**
1. **What:** Find the minimum day d such that we can form m bouquets, each made of k adjacent flowers that have bloomed by day d.
2. **Why:** Binary search applies because the predicate "can we make m bouquets by day d?" is monotonic in d (if possible by d, possible by any later day).
3. **How:** Binary search on [min(bloomDay), max(bloomDay)]. For each mid, scan array counting contiguous runs of bloomed flowers (bloomDay[i] ≤ mid); when a run length ≥ k, form a bouquet and reset count; check if total bouquets ≥ m.
4. **Challenges solved:** Finding minimum valid day without trying every day; checking feasibility in O(n) per guess.
5. **Pros and cons:** Pros: O(n log range), simple. Cons: Requires monotonic predicate; edge case n < m*k (return -1).
6. **Difference from alternatives:** Versus linear scan: binary search reduces tries. Versus greedy without binary search: we need the minimum d, so binary search is natural.
7. **Most common errors:** Forgetting n < m*k; resetting bouquet count on unbloomed flower but not when forming a bouquet (should reset to 0 after forming); wrong binary search bound (use min/max of array).

**Answer:** Binary search on the answer (day). Search space: [min(bloomDay), max(bloomDay)]. For a given day, check if we can form at least m bouquets of k adjacent flowers (only flowers that have bloomed by that day count). If we can, try a smaller day (high = mid - 1); otherwise try a larger day (low = mid + 1). Return the smallest day for which can_make(day) is true.

**Elaboration:** (1) **Why binary search?** The predicate "can we make m bouquets by day d?" is monotonic: if we can by day d, we can by any day ≥ d. So we can binary search for the minimum d. (2) **How to check can_make(day)?** Scan bloomDay left to right; count consecutive flowers that have bloomed (bloomDay[i] <= day). Whenever we have k consecutive, form one bouquet and reset the consecutive count to 0. If a flower hasn't bloomed, reset the count. Return true if total bouquets >= m. (3) **Edge case:** If n < m*k, impossible — return -1. (4) **Complexity:** O(n log(max_day - min_day)) for binary search and O(n) per check.

```python
def min_days(bloomDay: list[int], m: int, k: int) -> int:
    if len(bloomDay) < m * k:
        return -1

    def can_make(day: int) -> bool:
        bouquets, flowers = 0, 0
        for b in bloomDay:
            if b <= day:
                flowers += 1
                if flowers == k:
                    bouquets += 1
                    flowers = 0
            else:
                flowers = 0
        return bouquets >= m

    lo, hi = min(bloomDay), max(bloomDay)
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_make(mid):
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ans
# bloomDay=[1,10,3,10,2], m=3, k=1 → 3
```

---

### Q1.5 Jump Game – minimum/maximum steps or can reach end

**Source:** Adobe

**Answer:** Greedy. Track the farthest index reachable. If current index exceeds farthest, return false. Update farthest as `max(farthest, i + nums[i])`. If farthest >= n-1, return true. For minimum number of jumps, use a greedy: maintain current_reach and next_reach; when i exceeds current_reach, add one jump and set current_reach = next_reach; extend next_reach with i + nums[i]. **Elaboration:** The set of reachable indices is contiguous from 0, so we only need to track the farthest we can reach. For min jumps, one jump extends coverage from [0, current_reach] to [0, next_reach]; when we step past current_reach we must take another jump. O(n) time.

```python
def can_jump(nums: list[int]) -> bool:
    farthest = 0
    for i in range(len(nums)):
        if i > farthest:
            return False
        farthest = max(farthest, i + nums[i])
        if farthest >= len(nums) - 1:
            return True
    return True
# [2,3,1,1,4] → true; minimum jumps = 2
```

**Elaboration:** Reachable indices from 0 form a contiguous range; we only need to track the farthest. For min jumps: maintain current_reach and next_reach; when i > current_reach we take one more jump (current_reach = next_reach); always extend next_reach = max(next_reach, i + nums[i]). O(n).

---

### Q1.6 Find LCA (Lowest Common Ancestor) with key and level at each node

**Source:** Adobe

**Answer:** If nodes have a parent pointer and level: (1) Bring the deeper node up to the same level as the other by following parent links (level difference times). (2) Move both nodes up in lockstep until they point to the same node; that node is the LCA. Without parent pointers: first DFS from root to compute depth and parent for every node; then use the same "level up then meet" logic. Alternatively, a single DFS can return (found_p, found_q, lca): when the current node is p or q, return that; when both left and right subtrees return a non-null found, the current node is the LCA.

**Elaboration:** (1) **Why "level up then meet" works:** The LCA is the unique node that is an ancestor of both p and q and has the maximum depth. After leveling, both pointers are at the same depth; the first common ancestor as we go up is the LCA. (2) **Time:** O(h) with parent/level; O(n) for DFS to build parent/depth. (3) **Space:** O(1) with parent; O(n) or O(h) for recursion/stack.

---

### Q1.7 Longest substring without repeating characters

**Source:** Wipro (coding list)

**Structured answer:**
1. **What:** Longest contiguous substring that contains no duplicate characters.
2. **Why:** Classic sliding-window problem: we maintain a valid window [left, right] and expand/shrink to keep validity.
3. **How:** Right pointer expands; store last index of each char in a map. When s[right] is already in window (last_index >= left), move left to last_index+1; update last_index[s[right]]=right; track max length and start.
4. **Challenges solved:** Finding maximum valid window in one pass without enumerating all substrings.
5. **Pros and cons:** Pros: O(n) time, O(min(n, alphabet)) space. Cons: Assumes we can store last index per character.
6. **Difference from alternatives:** Versus brute force (check all substrings): O(n) vs O(n²). Versus set-only (no last index): we need last index to jump left correctly.
7. **Most common errors:** Not moving left to last_index+1 (only to left+1); forgetting last_index is valid only if ≥ left; off-by-one in length (right-left+1).

**Answer:** Sliding window with a hashmap storing the last seen index of each character. Expand the window by moving `right`; when s[right] was already seen and its last index is >= left (i.e. inside the current window), the window becomes invalid — move `left` to last_index[s[right]] + 1. Update last_index[s[right]] = right. At each step, the window [left..right] has no duplicates; track the maximum length and the start index of the best window.

**Elaboration:** (1) **Why sliding window?** We want a contiguous substring, so we maintain a valid segment [left, right] that has no repeating characters. (2) **Why move left to last_index+1?** So we remove the previous occurrence of the repeating character and the window is valid again. (3) **Time:** O(n); each character processed at most twice (once when right advances, once when left advances). (4) **Space:** O(min(n, alphabet size)) for the map.

```python
def longest_unique_substring(s: str) -> str:
    char_index = {}
    left = 0
    max_len, start = 0, 0
    for right in range(len(s)):
        if s[right] in char_index and char_index[s[right]] >= left:
            left = char_index[s[right]] + 1
        char_index[s[right]] = right
        if right - left + 1 > max_len:
            max_len = right - left + 1
            start = left
    return s[start:start + max_len]
```

---

### Q1.8 Longest palindromic substring (first if multiple)

**Source:** Wipro coding list

**Answer:** Expand around center. A palindrome has a center (or a "gap" between two chars for even length). For each index i, consider (1) odd-length palindrome centered at i: expand l, r from (i,i) while s[l]==s[r]. (2) Even-length centered between i and i+1: expand from (i, i+1). Keep the longest palindrome seen; if you need the first occurrence, compare by length only and keep the first when ties (so earlier centers win when lengths are equal).

**Elaboration:** (1) **Why expand around center?** Every palindrome has a unique center (or center gap). There are 2n-1 such centers (n for odd, n-1 for even). (2) **Correctness:** We try every possible center and compute the longest palindrome for that center in O(length); total O(n²). (3) **Manacher's algorithm** can do O(n) by reusing symmetry information; for interviews the O(n²) solution is usually sufficient.

```python
def longest_palindrome(s: str) -> str:
    def expand(l: int, r: int) -> str:
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l+1:r]
    best = ""
    for i in range(len(s)):
        odd = expand(i, i)
        even = expand(i, i + 1)
        for cand in (odd, even):
            if len(cand) > len(best):
                best = cand
    return best
# "forseeksskeesfor" → "seeksskees"
```

---

### Q1.9 Maximum length of contiguous subarray with equal 0s and 1s (and indices)

**Source:** Wipro coding list

**Answer:** Replace 0 with -1 so each element is +1 or -1. Then "equal 0s and 1s" means the subarray sum is 0. Use prefix sums: let p[i] = sum of first i elements (p[0]=0). Subarray (i+1..j) has sum p[j]-p[i]; we want p[j]-p[i]=0, i.e. p[j]=p[i]. So for each j, if we have seen the same prefix sum at index i, the length is j-i. Store the first index at which each prefix sum occurred; when we see a prefix sum again, update the max length and the (start, end) indices.

**Elaboration:** (1) **Why prefix sum?** Subarray sum (i..j) = p[j]-p[i-1] (or p[j+1]-p[i] depending on indexing). Sum zero means two prefix sums are equal. (2) **Why "first" index?** To maximize length we want the earliest index with the same prefix sum. (3) **Initialize:** first[0] = -1 so that a prefix sum 0 at index j gives length j-(-1)=j+1. (4) **Time:** O(n); **Space:** O(n) for the map.

```python
def max_len_equal_01(arr: list[int]) -> tuple[int, int, int]:
    # Returns (length, start, end)
    n = len(arr)
    p = 0
    first = {0: -1}
    length, start, end = 0, 0, 0
    for i in range(n):
        p += 1 if arr[i] == 1 else -1
        if p in first:
            if i - first[p] > length:
                length = i - first[p]
                start, end = first[p] + 1, i
        else:
            first[p] = i
    return (length, start, end)
# [1,0,1,1,1,0,0] → length=6, indices [1,6]
```

---

### Q1.10 Climbing stairs – number of ways (1 or 2 steps)

**Source:** Wipro coding list

**Answer:** Let f(n) = number of ways to reach step n. We can reach n from n-1 (one step) or from n-2 (two steps), so f(n) = f(n-1) + f(n-2). Base: f(0)=1 (one way: don't move), f(1)=1. This is the Fibonacci recurrence. Implement with two variables (a, b) and iterate to avoid O(n) space.

**Elaboration:** (1) **Why recurrence?** Optimal substructure: every way to reach n either ends with a 1-step from n-1 or a 2-step from n-2; no overlap. (2) **Why f(0)=1?** So that f(2)=f(1)+f(0)=1+1=2 (two ways: 1+1 or 2). (3) **Variants:** If order doesn't matter, it's just the number of 2s (and remaining 1s); if order matters, Fibonacci. (4) **Time O(n), Space O(1)** with rolling variables.

```python
def climb_stairs(n: int) -> int:
    a, b = 1, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
# n=4 → 5
```

---

### Q1.11 Find missing number in permutation of [1, n]

**Source:** Wipro coding list (array of size n-1, range [1,n], one missing)

**Answer:** (1) **Sum method:** The sum of 1+2+...+n is n(n+1)/2. The sum of the array is that minus the missing number. So missing = n(n+1)/2 - sum(arr). (2) **XOR method:** XOR of 1^2^...^n with XOR of all arr elements: each number 1..n except the missing appears once in each XOR, so they cancel; the missing number appears only in the first XOR. So missing = (1^2^...^n) ^ (arr[0]^...^arr[n-2]). Use n = len(arr)+1.

**Elaboration:** (1) **Why sum works:** Sum is linear; one missing value causes a fixed gap. (2) **Why XOR works:** x^x=0 and x^0=x; commutativity and associativity of XOR mean all paired numbers cancel. (3) **Overflow:** Sum can overflow for large n; XOR avoids overflow. (4) **Time O(n), Space O(1)**.

```python
def missing_number(arr: list[int]) -> int:
    n = len(arr) + 1
    return n * (n + 1) // 2 - sum(arr)
# [8,2,4,5,3,7,1] → 6
```

---

### Q1.12 Next permutation (lexicographic) for string/array

**Source:** Wipro coding list

**Answer:** (1) Scan from the right to find the first index i such that a[i] < a[i+1]. If no such i exists, the array is in descending order (last permutation); reverse the whole array to get the first permutation. (2) Otherwise, find the smallest index j > i such that a[j] > a[i] (so we choose the smallest "next" element to swap with). (3) Swap a[i] and a[j]. (4) Reverse the suffix a[i+1:] so that it is in ascending order (smallest possible for that suffix), giving the lexicographically next permutation.

**Elaboration:** (1) **Why this order?** Lexicographic order means we want the smallest change: find the rightmost position i where we can "increase" the value (a[i] < a[i+1]); then we must swap a[i] with the smallest element to the right that is larger than a[i], and then make the suffix as small as possible (sorted ascending). (2) **Why reverse?** After the swap, a[i+1:] is still in descending order; reversing makes it ascending. (3) **Time O(n), Space O(1)**.

```python
def next_permutation(arr: list) -> list:
    n = len(arr)
    i = n - 2
    while i >= 0 and arr[i] >= arr[i+1]:
        i -= 1
    if i < 0:
        return arr[::-1]
    j = n - 1
    while arr[j] <= arr[i]:
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    arr[i+1:] = reversed(arr[i+1:])
    return arr
# [c,d,e,f,g,h,i,j,a,b] → [c,d,e,f,g,h,i,j,b,a]
```

---

### Q1.13 Implement Autocomplete using Trie

**Source:** Google

**Answer:** A trie (prefix tree) has a root; each node has a map of character to child node and optionally `is_end` (whether a word ends here) and `freq` (frequency for ranking). **Insert:** For each character in the word, follow or create the child; at the last character set `is_end=True` and update frequency. **Autocomplete(prefix):** Follow the path for the prefix; if we cannot complete the path, return []. From the node at the end of the prefix, DFS (or BFS) to collect all descendant nodes where `is_end=True`, with their full strings and frequencies; sort by frequency and return top-k.

**Elaboration:** (1) **Why trie?** Prefix lookup is O(prefix length); no need to scan all words. (2) **Space:** O(total characters in all words); can be compressed (e.g. radix tree) for shared suffixes. (3) **Ranking:** Store frequency at the end node (or sum of frequencies for phrases); for typeahead we often want most popular completions. (4) **Alternatives:** For small vocabularies, sorted list + binary search; for fuzzy matching, consider n-gram index or Levenshtein automaton.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, freq: int = 1) -> None:
        node = self.root
        for c in word:
            node = node.children.setdefault(c, TrieNode())
        node.is_end = True
        node.freq += freq

    def search_prefix(self, prefix: str) -> list[str]:
        node = self.root
        for c in prefix:
            if c not in node.children:
                return []
            node = node.children[c]
        out = []
        def dfs(n, path):
            if n.is_end:
                out.append((path, n.freq))
            for c, ch in n.children.items():
                dfs(ch, path + c)
        dfs(node, prefix)
        return [w for w, _ in sorted(out, key=lambda x: -x[1])[:10]]
```

---

<a id="2-databases-apis"></a>
## 2. Databases & APIs

### Q2.1 ACID properties

**Source:** Tata Digital

**Structured answer:**
1. **What:** ACID = Atomicity (all-or-nothing), Consistency (valid state transitions), Isolation (concurrent transactions do not see uncommitted state), Durability (committed data survives crashes).
2. **Why:** Ensures data integrity and predictable behavior under concurrency and failures in relational databases.
3. **How:** Atomicity via undo log or WAL; consistency via constraints and application logic; isolation via locking or MVCC and isolation levels; durability via persisting WAL to disk before commit ack.
4. **Challenges solved:** Prevents partial writes (atomicity), invariant violations (consistency), dirty/phantom reads (isolation), and data loss (durability).
5. **Pros and cons:** Pros: Strong guarantees, easier reasoning. Cons: Cost in latency and availability; harder to scale horizontally.
6. **Difference from alternatives:** NoSQL often trades full ACID for availability and scale (eventual consistency, BASE). NewSQL aims for ACID + scale.
7. **Most common errors:** Assuming serializable when using weaker levels; ignoring constraint design (consistency); not handling deadlocks or retries.

**Answer:**

- **Atomicity:** Transaction either commits entirely or rolls back entirely (no partial commit).
- **Consistency:** Database moves from one valid state to another (constraints, invariants hold).
- **Durability:** Once committed, data survives crashes (written to durable storage).
- **Isolation:** Concurrent transactions do not see each other’s uncommitted state; isolation levels (read uncommitted, read committed, repeatable read, serializable) trade off consistency vs performance.

---

### Q2.2 Main features of NoSQL (4 V’s, CAP theorem)

**Source:** Tata Digital

**Answer:**

- **4 V’s:** Volume, Velocity, Variety, Veracity (big data characteristics).
- **CAP:** Among Consistency, Availability, Partition tolerance, you can only guarantee two under partition. NoSQL systems often choose AP (e.g. Cassandra) or CP (e.g. MongoDB in certain configs).
- **NoSQL features:** Schema flexibility, horizontal scaling, eventual consistency options, document/key-value/wide-column/graph models.

**Elaboration:** CAP: under partition we choose CP (e.g. MongoDB with majority) or AP (e.g. Cassandra). 4 V's drive design for volume/velocity/variety. PACELC extends CAP with latency vs consistency when there is no partition.

---

### Q2.3 How to maintain many-to-many relations

**Answer:** In relational DBs, use a **junction table** (associative entity / bridge table). Example: Students and Courses → create `Enrollments(student_id, course_id)` with foreign keys to both tables. The junction table holds pairs (s, c) for "student s is enrolled in course c." Optionally add attributes on the relationship (e.g. grade, enrolled_at). In document DBs: either embed an array of IDs in one side (e.g. student document has course_ids[]) and resolve in application, or store both and maintain consistency in application code. Junction table avoids duplication and keeps referential integrity in SQL.

**Elaboration:** (1) **Why not embed both?** In SQL, storing multiple FKs in one row (e.g. student with many course_ids) would require array columns or repeated rows; junction table is normalized and flexible. (2) **Queries:** "All courses for student S" → join Enrollments with Courses on course_id where student_id=S. "All students in course C" → join on student_id where course_id=C. (3) **Document DB:** Embedding in one document can lead to large arrays; if the "many" side is large, store the relationship in a separate collection or use references.

---

### Q2.4 Courses for which no students have been enrolled

**Source:** Tata Digital

**Answer:** We need courses that have zero enrollments. (1) **LEFT JOIN:** Left join Courses to Enrollments on course_id. For courses with no enrollments, the Enrollments columns will be NULL. Filter WHERE e.student_id IS NULL (or any Enrollments column IS NULL). (2) **NOT EXISTS:** For each course, check that there does not exist any row in Enrollments with that course_id. Often better optimized by the planner. (3) **NOT IN:** SELECT courses where id NOT IN (SELECT course_id FROM Enrollments). Careful with NULLs in subquery (can filter out rows incorrectly); NOT EXISTS is safer.

**Elaboration:** (1) **Why LEFT JOIN?** We want all courses (left side); when there is no matching enrollment, the right side is NULL. (2) **Why NOT EXISTS over NOT IN?** If the subquery returns NULL, "id NOT IN (..., NULL)" evaluates to UNKNOWN in SQL and the row is excluded. NOT EXISTS avoids that. (3) **Performance:** NOT EXISTS can short-circuit (stop at first match); index on Enrollments(course_id) helps.

```sql
SELECT c.id, c.name FROM Courses c
LEFT JOIN Enrollments e ON c.id = e.course_id
WHERE e.student_id IS NULL;
```

---

### Q2.5 GET vs POST; retry on failure for both

**Source:** Tata Digital

**Structured answer:**
1. **What:** GET = read-only, params in URL, idempotent and safe. POST = create/update/action, body in request, not idempotent.
2. **Why:** GET for reads (cacheable, bookmarkable); POST for mutations. Retry: GET safe to retry; POST needs idempotency keys or care to avoid duplicates.
3. **How:** GET: no body; use query params. POST: send body (JSON/form); use idempotency key header for safe retries. Retry with exponential backoff; for POST store key → response and return same on replay.
4. **Challenges solved:** Clear semantics (read vs write); safe retries (GET); duplicate prevention (POST with idempotency key).
5. **Pros and cons:** GET: Pros: Cacheable, simple. Cons: URL length limit, no secret in URL. POST: Pros: No URL limit, body for complex data. Cons: Not cacheable by default; retry can duplicate.
6. **Difference from alternatives:** PUT often idempotent (replace at URI); PATCH partial update. Idempotency key vs no key: with key, retries return stored response.
7. **Most common errors:** Retrying POST without idempotency (double charge/duplicate); putting secrets in GET URL; not using 429/503 to signal when to retry.

**Answer:**

- **GET:** Idempotent (multiple identical requests have the same effect as one) and **safe** (no server state change). Parameters in URL; cacheable by default. Use for reads. **POST:** Not idempotent (sending twice can create two resources); request body; use for create, update, or actions. Not cacheable by default.
- **Retry:** **GET:** Safe to retry; no side effects. **POST:** Retrying can cause duplicate creates or double charges. Mitigations: (1) **Idempotency key:** Client sends a key (e.g. UUID) in header; server stores (key → response); on retry with same key, return stored response without re-executing. (2) Avoid automatic retries for POST on 5xx unless you use idempotency; use exponential backoff for 503/429. (3) Design APIs to be idempotent where possible (e.g. "set status to X" instead of "increment").

**Elaboration:** (1) **Why idempotency matters:** Networks and clients fail; retries are common. Idempotent operations avoid duplicate side effects. (2) **PUT vs POST:** PUT is often idempotent (replace resource at URI); POST creates and is not. (3) **Idempotency key implementation:** Store in DB or cache with TTL; key scope can be per-user or global; return 409 if key reused with different body.

---

<a id="3-async-concurrency-backend"></a>
## 3. Async, Concurrency & Backend

### Q3.1 async/await vs 10 workers; two steps where step 2 depends on step 1

**Source:** Tata Digital

**Structured answer:**
1. **What:** Sync workers = one thread per request, blocks on I/O. Async/await = one or few threads multiplex many requests by yielding during I/O. Step 2 depends on step 1 (e.g. DB result) in both.
2. **Why:** With sync, 10 workers = at most 10 concurrent requests; if step 1 is I/O-bound, CPU is underused. Async allows many in-flight requests per thread when I/O dominates.
3. **How:** Sync: request → thread runs step 1 (blocks) → step 2 → response. Async: request → coroutine awaits step 1 (yields) → event loop runs others → step 1 done → run step 2 → response.
4. **Challenges solved:** Throughput under I/O-bound load; resource use (fewer threads with async).
5. **Pros and cons:** Sync workers: Pros: Simple, step order obvious. Cons: One request per thread; many threads if many concurrent. Async: Pros: Many requests per thread; less memory. Cons: CPU-bound work still blocks; need async-friendly libraries.
6. **Difference from alternatives:** Async vs sync: async multiplexes; sync blocks. Async vs multiprocessing: async for I/O; multiprocessing for CPU-bound. Step 2 after step 1: same ordering in both; async does not change per-request order.
7. **Most common errors:** Using async for CPU-bound (still single-threaded); blocking the event loop with sync I/O; forgetting to await; mixing sync and async incorrectly.

**Answer:** With **10 workers (sync):** Each worker blocks on I/O during step 1; when step 1 finishes, it does step 2. So at most 10 requests in progress; CPU is underutilized if step 1 is I/O-bound. With **async/await:** One (or few) process can handle many requests by yielding during I/O; when step 1 (e.g. DB call) completes, the same worker runs step 2. So you can have many more concurrent “in-flight” requests with fewer OS threads. If step 2 depends on step 1, ordering is preserved per request in both models; async gives better throughput when I/O is the bottleneck because you don’t block a thread waiting.

---

### Q3.2 What is FastAPI; why “fast”

**Source:** Gen/AI interviewer

**Answer:** FastAPI is a modern Python web framework for APIs. “Fast” refers to (1) **high performance** (on par with Node/Go due to ASGI and Starlette), (2) **fast development** (automatic OpenAPI docs, Pydantic validation, type hints). It uses async support and dependency injection, making it a common choice for ML inference APIs.

---

<a id="4-kafka-messaging"></a>
## 4. Kafka & Messaging

### Q4.1 DLQ (Dead Letter Queue) architecture

**Source:** Zzazz

**Structured answer:**
1. **What:** A Dead Letter Queue (DLQ) is a destination where messages are sent after they fail processing repeatedly (e.g. after N retries).
2. **Why:** To avoid losing failed messages and to keep the main pipeline unblocked so other messages can be processed.
3. **How:** Consumer fails → retry (same topic or dedicated retry topic with delay) → after max retries, publish to DLQ; separate process inspects/replays or alerts.
4. **Challenges solved:** Preserves failed messages for debugging/replay; prevents one bad message from blocking the consumer; separates healthy flow from failure handling.
5. **Pros and cons:** Pros: No message loss; clear failure visibility; main topic stays clean. Cons: Need to operate and monitor DLQ; replay logic and idempotency required.
6. **Difference from alternatives:** Versus retry-only: DLQ gives a permanent place for failures. Versus drop: no loss. Versus blocking: pipeline continues.
7. **Most common errors:** Not making main consumer idempotent (replay causes duplicates); forgetting to monitor DLQ depth; not setting max retries and ending in infinite retry.

**Answer:** When a message fails processing after N retries, send it to a **Dead Letter Queue (DLQ)**. Flow: Consumer reads from main topic → process fails → retry (optional retry topic or same topic with delay) → after max retries, publish to DLQ. A separate process can inspect DLQ, fix data or alert. This keeps the main topic clean and allows replay/fix without blocking the pipeline.

**Elaboration:** (1) **Why DLQ?** Failed messages would otherwise block the consumer (if we don't commit and keep retrying) or be lost (if we commit and skip). DLQ preserves them for later analysis or replay. (2) **Retry options:** Same topic (consumer sleeps and re-fetches) can cause head-of-line blocking; a separate retry topic with a delay (e.g. consumer that republishes to main after T seconds) isolates failures. (3) **Idempotency:** Ensure the main consumer is idempotent so that replay from DLQ (after fix) doesn't duplicate side effects. (4) **Monitoring:** Alert on DLQ depth; track failure reasons (e.g. by header) to spot systemic issues.

---

### Q4.2 How to implement retry in Kafka

**Answer:** (1) **Consumer-side:** Catch exception, don’t commit offset; sleep and re-fetch (same message again). (2) **Retry topic:** Publish failed message to `topic-retry` with backoff timestamp; a consumer reads when timestamp has passed and republishes to main or processes. (3) **Exponential backoff:** Increase delay between retries. (4) **Idempotent processing:** So retries don’t double-apply side effects.

---

### Q4.3 Consumer group vs partition

**Source:** Zzazz

**Answer:** **Partition:** Unit of parallelism and ordering within a topic; each partition is an ordered log. **Consumer group:** Set of consumers that share the workload; each partition is assigned to at most one consumer in the group. So # of consumers in a group can be up to # of partitions for max parallelism. More partitions = more parallelism; ordering is per partition only.

**Elaboration:** (1) **Partition:** Messages in a partition are ordered; keys (if provided) determine which partition a message goes to (hash(key) % num_partitions). So same key → same partition → order preserved for that key. (2) **Consumer group:** The broker assigns each partition to exactly one consumer in the group (rebalance when consumers join/leave). So max parallelism = number of partitions; having more consumers than partitions leaves some idle. (3) **Scaling:** To scale consumption, add partitions and add consumers (up to that number). Adding partitions is possible but can change key→partition mapping; plan partition count upfront for key-based ordering. (4) **Ordering guarantee:** Only within a partition; if you need global order, use one partition (and lose parallelism) or order by key so that related messages share a partition.

---

<a id="5-search-storage"></a>
## 5. Search & Storage (Elasticsearch, MongoDB)

### Q5.1 How MongoDB performs update behind the scenes

**Source:** Zzazz

**Answer:** MongoDB stores documents in BSON. Update can be in-place if the document size doesn’t grow (e.g. set a field). If the document grows (e.g. array append), it may need to **move** the document to a new location and update the index (pointers). This can cause fragmentation; background compacting helps. Indexes are updated for the modified fields (see Q5.2).

**Elaboration:** (1) **In-place update:** If the document size does not change (e.g. set a field to a new value of same size), MongoDB can overwrite in place; indexes on that field are updated. (2) **Document growth:** If the document grows (e.g. push to array), it may not fit in the same disk slot; MongoDB moves it to a new location and updates all indexes that point to it. This causes fragmentation and extra I/O. (3) **Padding:** Older versions used padding to reduce moves; current versions use power-of-two allocation. (4) **Compaction:** Background compaction reclaims space and defragments; avoid long-running in-place updates that grow docs repeatedly.

---

### Q5.2 How indexes update in Elasticsearch when millions of records are updated

**Source:** Zzazz

**Structured answer:**
1. **What:** Elasticsearch (Lucene) uses inverted indexes. An "update" is implemented as delete (mark old doc) + index (write new doc); segments are immutable.
2. **Why:** Immutability simplifies concurrency and crash recovery; merging and compaction handle old segments over time.
3. **How:** Update request → delete old doc in segment (mark deleted) + write new doc to new segment; refresh makes it searchable (default ~1s); background merge merges segments and purges deletes.
4. **Challenges solved:** Consistent reads; efficient bulk updates when using bulk API and tuning refresh/merge.
5. **Pros and cons:** Pros: No in-place lock; good for append-heavy and bulk. Cons: More disk and I/O during large updates; eventual visibility (refresh interval).
6. **Difference from alternatives:** Versus DB in-place update: ES always append/delete. Versus no refresh: set refresh_interval=-1 during bulk to avoid refresh cost, then refresh once.
7. **Most common errors:** Not using bulk API for 5M docs; leaving refresh at 1s during bulk (thrashing); not tuning merge policy (I/O spikes); expecting immediate visibility.

**Answer:** ES uses **inverted indexes**. Updates are implemented as delete + index (documents are immutable in Lucene). So a bulk update of 5M docs causes new segments to be written and old segments marked deleted; segments are merged in the background. Indexing is eventually consistent (refresh interval, e.g. 1s). For large updates, use bulk API and tune refresh_interval and merge policy to avoid load spikes.

**Elaboration:** (1) **Why delete + index:** Lucene segments are immutable; you cannot update a document in place. So an "update" is a delete (mark old doc as deleted) plus index (write new doc to a new segment). (2) **Segments:** New documents go into new segments; old segments are marked with deletes. Background merge combines segments and purges deletes. (3) **Refresh:** By default every 1s, the index is refreshed (new segments made searchable). For bulk indexing you can set refresh_interval to -1 and refresh manually at the end to avoid refresh overhead. (4) **5M docs:** Use bulk API (e.g. 1000–5000 docs per bulk request), disable refresh during bulk, then refresh; tune merge policy (e.g. merge throttling) to avoid I/O spikes.

---

### Q5.3 What is ANN in Elasticsearch?

**Source:** Zzazz

**Answer:** **Approximate Nearest Neighbor (ANN)** search: for vector/knn search, ES (e.g. with dense_vector and knn search) uses approximate algorithms (e.g. HNSW) to find similar vectors without comparing to every vector. Trade-off: speed and scalability vs exact recall. Used for semantic search, recommendations.

**Elaboration:** (1) **Exact k-NN** compares the query vector to every vector (O(n)); fine for small n, not for millions. (2) **ANN** approximates k-NN with indexes like HNSW (graph-based) or IVF (vector quantization); trade recall for speed. (3) **HNSW:** Hierarchical Navigable Small World; build a graph where similar vectors are connected; search by greedy traversal. (4) **Tuning:** Higher ef_search/ef_construction improves recall but increases latency and build time. (5) **dense_vector + knn in ES:** Store vectors in the mapping; at search time use kNN search with approximate algorithm; filter by metadata can be applied before or after vector search depending on the API.

---

### Q5.4 Sharding; what to consider for availability in system design

**Source:** Zzazz

**Answer:** **Sharding:** Partition data across nodes (e.g. by key range or hash) to scale storage and read/write load. **Availability considerations:** Replication (replica shards), multi-AZ deployment, failure detection and failover, consistency model (strong vs eventual), and how to rebalance when adding/removing nodes.

**Elaboration:** (1) **Sharding strategies:** Hash-based (even distribution; range queries need scatter-gather); range-based (good for range queries; risk of hot shards). (2) **Availability:** Replicate each shard (e.g. 1 primary + N replicas); if a node fails, a replica is promoted. Multi-AZ deploys replicas in different zones. (3) **Consistency:** Strong consistency (read from primary or quorum) vs eventual (read from any replica; may see stale data). (4) **Rebalancing:** When adding nodes, move some shards to new nodes; when removing, reassign shards. Plan for minimal data movement and avoid overload during rebalance. (5) **Monitoring:** Shard allocation, disk usage per shard, query routing, and failure detection (e.g. heartbeat).

---

<a id="6-ml-fundamentals-statistics"></a>
## 6. ML Fundamentals & Statistics

### Q6.1 Prior, posterior, marginal likelihood (Bayesian)

**Source:** BalanceHero

**Structured answer:**
1. **What:** Prior = belief about parameters before data; Likelihood = P(data|params); Posterior = updated belief after data, P(θ|D) ∝ P(D|θ)P(θ); Marginal likelihood = P(D) = ∫ P(D|θ)P(θ)dθ (normalizing constant).
2. **Why:** Bayesian framework provides uncertainty quantification, incorporation of prior knowledge, and principled model comparison via marginal likelihood or Bayes factors.
3. **How:** Specify prior and likelihood; posterior ∝ likelihood × prior; marginal likelihood integrates over θ; for inference use MCMC or variational methods when not closed-form.
4. **Challenges solved:** Quantifies uncertainty; uses prior knowledge; compares models (Bayes factors); avoids overfitting via Occam's razor in marginal likelihood.
5. **Pros and cons:** Pros: Full posterior; natural for small data and priors. Cons: Prior choice subjective; computation often intractable (need MCMC/VI).
6. **Difference from alternatives:** Versus frequentist: Bayesian gives a distribution over θ; frequentist gives point estimates and CIs. Versus MLE: MLE is mode of posterior with flat prior; Bayesian keeps full posterior.
7. **Most common errors:** Using improper priors that make marginal likelihood undefined; ignoring posterior correlation; confusing prior with likelihood; not checking convergence in MCMC.

**Answer:**

- **Prior P(θ):** Belief about parameters θ before seeing data. Encodes domain knowledge or non-informativeness (e.g. uniform, Jeffreys prior).
- **Likelihood P(D|θ):** Probability of observing the data D given parameters θ. The model of how data are generated.
- **Posterior P(θ|D):** Belief about θ after seeing D. By Bayes' rule: P(θ|D) = P(D|θ) P(θ) / P(D); i.e. posterior ∝ likelihood × prior. Updated belief combining data and prior.
- **Marginal likelihood P(D):** P(D) = ∫ P(D|θ) P(θ) dθ. Normalizing constant so that posterior integrates to 1. Used in model comparison: ratio of marginal likelihoods (Bayes factor) compares two models.

**Elaboration:** (1) **Why Bayesian?** We get a full distribution over parameters (uncertainty quantification), natural incorporation of prior knowledge, and principled model comparison. (2) **Conjugate priors:** When prior and posterior are in the same family (e.g. Beta-Binomial), inference is closed-form. (3) **When intractable:** Use MCMC (e.g. Gibbs, HMC) or variational inference to approximate the posterior. (4) **Marginal likelihood** penalizes model complexity (Occam's razor) because complex models spread probability over more parameter space.

---

### Q6.2 Linear regression assumptions

**Source:** Real, Zzazz

**Structured answer:**
1. **What:** Linear regression models E[y|X] = Xβ under assumptions: linearity, independence of errors, homoscedasticity, no perfect multicollinearity, and (for inference) normality of errors.
2. **Why:** When these hold, OLS is BLUE (best linear unbiased) and inference (t-tests, CIs) is valid.
3. **How:** Fit by minimizing sum of squared residuals; estimate β = (X'X)^{-1}X'y; check assumptions via residual plots, tests (e.g. Breusch–Pagan for heteroscedasticity), and VIF for multicollinearity.
4. **Challenges solved:** Provides interpretable coefficients and valid inference when the data-generating process matches the assumptions.
5. **Pros and cons:** Pros: Simple, interpretable, closed-form, well-understood. Cons: Sensitive to violations; only captures linear relationships.
6. **Difference from alternatives:** Versus GLM: GLM allows non-normal y (e.g. logistic, Poisson). Versus robust regression: robust relaxes normality and handles outliers. Versus regularized (Ridge/Lasso): adds penalty for stability/selection.
7. **Most common errors:** Ignoring heteroscedasticity (wrong SEs); ignoring multicollinearity (unstable coefficients); extrapolating beyond X range; confusing correlation with causation.

**Answer:** (1) **Linearity:** E[y|X] = Xβ; the mean of y is a linear combination of predictors. (2) **Independence:** Errors (residuals) are independent across observations (no autocorrelation, no clustered structure). (3) **Homoscedasticity:** Var(ε) is constant (no heteroscedasticity). (4) **No perfect multicollinearity:** No predictor is a linear combination of others (so X'X is invertible). (5) **Normality of errors:** For inference (t-tests, F-tests, CIs), errors are often assumed normal; OLS is still BLUE under 1–4 without normality, but inference relies on large-sample asymptotics or normality.

**Elaboration:** **Violations and fixes:** Non-linearity → transform predictors or y (log, sqrt), or add polynomial/ spline terms. Heteroscedasticity → robust standard errors (sandwich), or WLS. Autocorrelation → time-series models (ARIMA) or cluster-robust SE. Multicollinearity → drop or combine predictors, or regularization (Ridge). Non-normal errors → use GLM (e.g. Poisson, Binomial) or robust inference.

---

### Q6.3 R-squared and how to calculate it

**Source:** BalanceHero

**Structured answer:**
1. **What:** R² (coefficient of determination) is the proportion of the variance in the dependent variable (y) that is explained by the model. Formula: R² = 1 - (SS_res / SS_tot), where SS_res = Σ(y_i - ŷ_i)² (residual sum of squares) and SS_tot = Σ(y_i - ȳ)² (total sum of squares). Range: 0 to 1 (or negative if the model is worse than predicting the mean).
2. **Why:** It gives a single, interpretable measure of how well the model fits the data relative to always predicting the mean. Used to compare models and communicate fit quality to non-experts.
3. **How:** Compute predictions ŷ_i; SS_res = sum of squared residuals; SS_tot = sum of squared deviations of y from its mean; R² = 1 - SS_res/SS_tot. Adjusted R² = 1 - (1 - R²)(n - 1)/(n - p - 1) to penalize adding predictors (p = number of predictors, n = sample size).
4. **Challenges solved:** Summarizes fit in one number; adjusted R² helps compare models with different numbers of predictors.
5. **Pros and cons:** Pros: Easy to interpret (e.g. "model explains 85% of variance"); scale-free; widely used. Cons: Can be misleading (high R² with wrong model; sensitive to outliers); does not indicate causation; adding predictors always increases R² (use adjusted R²).
6. **Difference from alternatives:** Versus RMSE/MAE: R² is scale-free and relative to the mean model. Versus adjusted R²: adjusted R² penalizes extra variables. Versus F-statistic: F tests overall significance; R² measures effect size.
7. **Most common errors:** Interpreting R² as "good" without checking residuals or assumptions; using R² for non-linear or classification models without care; ignoring that R² increases with more predictors (use adjusted R²); assuming high R² means good out-of-sample performance.

**Applications of R²:**
- **Model comparison:** Compare linear (or other) regression models on the same dataset; higher R² (or adjusted R²) suggests better fit.
- **Variable selection:** Use change in R² (or adjusted R²) when adding/removing predictors to decide if a variable helps.
- **Reporting fit:** Standard metric in reports and papers for regression (e.g. economics, social sciences, forecasting).
- **Quality assurance:** Monitor R² in production regression models as a drift or degradation signal (e.g. R² drops on new data).
- **Baseline comparison:** R² = 0 means no better than predicting ȳ; R² < 0 means worse than the mean baseline.

**Answer:** R² = 1 - (SS_res / SS_tot), where SS_res = Σ(y_i - ŷ_i)², SS_tot = Σ(y_i - ȳ)². Proportion of variance explained. Adjusted R² penalizes extra predictors.

```python
def r_squared(y_true, y_pred):
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
```

---

### Q6.4 Fit Linear Regression from scratch / value of coef_ and intercept_

**Source:** BalanceHero

**Answer:** Closed form: β = (X'X)^{-1} X'y. For X = [[1],[2],[3],[4]], y = [2,4,6,8], true relationship y = 2x, so coef_ ≈ 2, intercept_ ≈ 0.

```python
from sklearn.linear_model import LinearRegression
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])
model = LinearRegression().fit(X, y)
# model.coef_ ≈ [2.], model.intercept_ ≈ 0.
```

---

### Q6.5 Entropy

**Source:** Zzazz

**Answer:** **Definition:** For a discrete distribution p, entropy H(p) = -Σ p(x) log p(x) (usually log base 2; units are bits). Measures **uncertainty** or **information content**: higher entropy means more uncertainty. **In ML:** (1) **Decision trees:** Split that most reduces impurity (entropy or Gini) is chosen; goal is to make child nodes purer. (2) **Cross-entropy loss:** For classification, H(p, q) = -Σ p(x) log q(x); when p is the true label (one-hot) and q is the predicted probability, minimizing cross-entropy is equivalent to MLE. (3) **KL divergence:** KL(p||q) = H(p, q) - H(p); measures difference between distributions.

**Elaboration:** (1) **Why log?** So that independent events add information (bits). (2) **Maximum entropy:** Uniform distribution has maximum entropy for a given support. (3) **Gini impurity:** 1 - Σ p_i² is another split criterion; both favor pure nodes. (4) **Continuous case:** Differential entropy; for Gaussians, entropy is 0.5 log(2πe σ²).

---

### Q6.6 Regularization techniques

**Source:** Zzazz, Wipro list

**Structured answer:**
1. **What:** Techniques that constrain model complexity: L1 (Lasso), L2 (Ridge), Elastic Net, dropout (DL), early stopping.
2. **Why:** Reduce overfitting (high variance) and improve generalization by limiting effective capacity or encouraging simpler solutions.
3. **How:** L1/L2: add penalty to loss; fit with penalized optimization. Dropout: zero random activations in training; scale at test. Early stopping: stop when validation loss stops improving.
4. **Challenges solved:** Overfitting; instability with correlated features (L2); feature selection (L1); co-adaptation in neural nets (dropout).
5. **Pros and cons:** L1: Pros: Sparsity, feature selection. Cons: Unstable with correlated features. L2: Pros: Stable, shrinks coefficients. Cons: No exact zeros. Dropout: Pros: Ensemble effect. Cons: Longer training; need to tune p.
6. **Difference from alternatives:** L1 vs L2: L1 gives sparse solutions; L2 shrinks uniformly. Dropout vs weight decay: different mechanism (random mask vs penalty). AdamW: decoupled weight decay vs L2 in loss for adaptive optimizers.
7. **Most common errors:** Too strong regularization (underfit); forgetting to turn off dropout at inference or scale; using L2 in Adam instead of AdamW weight decay; no validation set for early stopping.

**Answer:** **L1 (Lasso):** Penalty λ Σ|β_j|. Shrinks some coefficients to exactly zero → **sparsity**, useful for feature selection. **L2 (Ridge):** Penalty λ Σ β_j². Shrinks all coefficients toward zero; no exact zeros; helps when predictors are correlated. **Elastic Net:** α L1 + (1-α) L2; combines sparsity and stability. **Dropout (DL):** During training, randomly set a fraction p of activations to zero; at test time scale by (1-p) or use all units. Reduces co-adaptation of neurons; acts like an ensemble. **Early stopping:** Stop training when validation loss stops improving; limits effective capacity. **Purpose:** Reduce overfitting (high variance) and improve generalization.

**Elaboration:** (1) **Why L1 gives sparsity:** The L1 ball has corners on the axes; the optimal solution under L1 often lies on a corner (some β_j = 0). (2) **Why L2 doesn't:** The L2 ball is smooth; shrinkage is spread across all coefficients. (3) **Dropout:** Training with dropout is like training many thinned networks and averaging; at test time we approximate the geometric mean of their predictions. (4) **Weight decay vs L2:** In SGD, L2 penalty is equivalent to weight decay (decay each weight by a factor each step); in Adam, L2 in the loss is not equivalent to weight decay, hence AdamW uses decoupled weight decay.

---

### Q6.7 Bias–variance tradeoff; diagnose high bias vs high variance

**Source:** Wipro list

**Structured answer:**
1. **What:** Bias = error from wrong/simple assumptions (underfitting). Variance = error from sensitivity to the training set (overfitting). Tradeoff: as complexity increases, bias usually decreases and variance increases.
2. **Why:** Understanding which dominates guides the fix: add capacity vs regularize/get more data.
3. **How:** Diagnose with learning curves (train vs val error vs sample size or iterations). High bias: both train and val error high. High variance: train low, val high. Fix bias: more features, more complex model, less regularization. Fix variance: more data, regularization, simplify, dropout/early stop.
4. **Challenges solved:** Explains underfitting vs overfitting; guides model selection and tuning.
5. **Pros and cons:** Conceptual framework: Pros: Clear actions. Cons: In practice both can be present; decomposition is theoretical (squared error = bias² + variance + irreducible).
6. **Difference from alternatives:** Bias vs variance: bias = systematic error; variance = variability across samples. Versus "overfitting": overfitting is high variance; underfitting is high bias.
7. **Most common errors:** Adding complexity when variance is high (makes it worse); only looking at train error; not using validation set; ignoring irreducible error.

**Answer:** **Bias:** The error due to the model's wrong or simplistic assumptions; the model systematically misses the true relationship (underfitting). **Variance:** The error due to the model's sensitivity to the particular training set; different training sets would give very different fits (overfitting). **Tradeoff:** As model complexity increases, bias typically decreases and variance increases; we want to find the sweet spot. **Diagnosis:** **High bias:** Both training and validation error are high; model is too simple. Fix: add features, use a more complex model, or reduce regularization. **High variance:** Training error is low but validation error is high; model has memorized the training set. Fix: more data, stronger regularization, simplify the model, or use dropout/early stopping. **Learning curves:** Plot train and validation error vs sample size (or training iterations); if val error is much higher than train, variance dominates; if both are high, bias dominates.

**Elaboration:** (1) **Decomposition:** For squared error, E[(y - ŷ)²] = Bias² + Variance + Irreducible error. (2) **Why more data helps variance:** With more data, the model's fit is less dependent on the particular sample. (3) **Cross-validation** gives an estimate of variance (different folds give different scores). (4) **In deep learning:** Often we have low bias (model can fit training well) and must control variance with regularization, data augmentation, and enough data.

---

### Q6.8 Missing value imputation – why code fails

**Source:** BalanceHero (code with `sum(feature)/len(feature)` for imputation)

**Answer:** If `feature` contains `None`, `sum(feature)` fails (can’t add None). Also `len(feature)` counts NaNs/None, so mean is wrong. Fix: filter out None/NaN before sum, or use `np.nanmean`; then fill missing with that mean. Example:

```python
def impute_missing_values(data):
    transposed = list(zip(*data))
    imputed = []
    for feature in transposed:
        values = [x for x in feature if x is not None]
        mean_val = sum(values) / len(values) if values else 0
        imputed.append([x if x is not None else mean_val for x in feature])
    return [list(row) for row in zip(*imputed)]
```

---

<a id="7-ensemble-methods-tree-models"></a>
## 7. Ensemble Methods & Tree Models

### Q7.1 Bagging vs Boosting

**Source:** Zzazz, Wipro

**Structured answer:**
1. **What:** Bagging = train many models on bootstrap samples, then average or vote. Boosting = train models sequentially, each correcting previous errors; weighted combination.
2. **Why:** Bagging reduces variance without increasing bias; boosting reduces bias (and can reduce variance with regularization) to improve accuracy.
3. **How:** Bagging: sample with replacement → train base learner → average. Boosting: fit to residuals or reweighted data → add to ensemble with weight → repeat.
4. **Challenges solved:** Bagging tackles high variance (e.g. deep trees); boosting tackles bias and residual error.
5. **Pros and cons:** Bagging: Pros: Parallel, stable, less overfitting. Cons: Does not reduce bias. Boosting: Pros: Often higher accuracy. Cons: Sequential, can overfit; needs tuning (depth, LR, early stop).
6. **Difference from alternatives:** Bagging vs Boosting: bagging is parallel and variance-reducing; boosting is sequential and bias-reducing. Stacking combines multiple base models with a meta-learner.
7. **Most common errors:** Boosting: too many rounds (overfit), no early stopping, forgetting to tune learning rate. Bagging: too few trees or too deep trees.

**Answer:** **Bagging:** Train many models on bootstrap samples; average (regression) or vote (classification). Reduces variance; e.g. Random Forest. **Boosting:** Train sequentially; each model corrects previous errors (e.g. fit residuals); weighted combination. Reduces bias and variance with care; e.g. AdaBoost, GBM, XGBoost.

**Elaboration:** (1) **Bagging:** Bootstrap = sample with replacement from the training set; each model sees a different sample, so predictions are less correlated. Averaging reduces variance (no change in bias). Trees are ideal because they have high variance and low bias. (2) **Boosting:** Each new model focuses on mistakes of the ensemble so far (e.g. fit residuals in GBM, or reweight misclassified points in AdaBoost). Bias decreases; variance can increase, so regularization (depth, learning rate, early stopping) is important. (3) **When to use:** Bagging (Random Forest) when you want robustness and parallel training; boosting (XGBoost, etc.) when you want maximum accuracy and can tune carefully. (4) **Stacking:** Meta-learner on top of base models; can combine bagging and boosting or different algorithms.

---

### Q7.2 XGBoost and CatBoost – architecture, when to use, differences

**Source:** Wipro

**Structured answer:**
1. **What:** Both are gradient boosting (additive decision trees). XGBoost: second-order gradients, L1/L2 on leaves, column subsampling. CatBoost: ordered boosting, symmetric trees, native categorical handling.
2. **Why:** Gradient boosting often wins on tabular data; XGBoost and CatBoost add regularization and efficiency; CatBoost reduces overfitting and handles categories without manual encoding.
3. **How:** Iteratively fit trees to the negative gradient (or residual); add to ensemble with learning rate. XGBoost: histogram-based split finding, handles missing. CatBoost: permutation-based target encoding, ordered boosting to avoid leakage.
4. **Challenges solved:** Accuracy on tabular data; overfitting (regularization, early stop); categorical features (CatBoost); missing values (XGBoost).
5. **Pros and cons:** XGBoost: Pros: Fast, robust, good defaults. Cons: Categoricals need encoding. CatBoost: Pros: Great for categoricals, less overfitting on small data. Cons: Slower than XGBoost in some settings. Both: tuning (depth, LR, rounds) matters.
6. **Difference from alternatives:** XGBoost vs CatBoost: CatBoost has ordered boosting and native categoricals; XGBoost more common in general. Both vs Random Forest: boosting is sequential and often more accurate; RF is parallel and simpler. vs LightGBM: leaf-wise growth, often faster.
7. **Most common errors:** Too many rounds without early stopping; not tuning learning rate and depth; using default categorical handling in XGBoost when many categories; leaking labels in manual target encoding (CatBoost avoids this).

**Answer:** Both are **gradient boosting** (additive trees). **XGBoost:** Second-order gradient, regularization, handles missing values, fast. **CatBoost:** Ordered boosting, native categorical handling, less overfitting on small data. **When:** XGBoost for general tabular; CatBoost when you have many categoricals and want minimal preprocessing. Differences: splitting (CatBoost uses ordered target encoding), GPU support, default params.

**Elaboration:** (1) **Gradient boosting:** Additive model F(x) = F_{m-1}(x) + η·h_m(x); each h_m is a tree fitted to the negative gradient (or residual) of the loss. XGBoost uses second-order (Newton) approximation for the loss; adds L1/L2 on leaves. (2) **XGBoost:** Handles missing values (learn best direction at split); column subsampling; fast histogram-based split finding. (3) **CatBoost:** Ordered boosting (permutation-based target encoding to avoid leakage); symmetric trees (same split structure in a level); often better on small data and many categoricals. (4) **When to use:** XGBoost for general tabular, large data; CatBoost when you have many categoricals and want minimal preprocessing or slightly better default behavior. (5) **LightGBM:** Leaf-wise growth, histogram, often faster; compare all three with tuning.

---

### Q7.3 Feature importance – how to calculate and best practices

**Source:** Wipro

**Answer:** (1) **Tree-based:** Gini/entropy reduction or MSE reduction per feature (sum over splits). (2) **Permutation importance:** Shuffle feature, measure drop in metric. (3) **SHAP:** Shapley values for per-sample attribution. Best practice: use multiple methods (e.g. permutation + SHAP) and validate on hold-out; be aware of correlation (importance can be split across correlated features).

**Elaboration:** (1) **Tree-based (impurity reduction):** Sum the decrease in Gini/entropy (or MSE for regression) every time a feature is used to split; normalize by total. Fast but biased toward high-cardinality and correlated features. (2) **Permutation importance:** Shuffle the feature column (breaks relationship with target); measure drop in metric (e.g. accuracy). Unbiased but expensive (one pass per feature). (3) **SHAP:** Shapley values from game theory; fair attribution of prediction to each feature per sample. Satisfies consistency and local accuracy. Use tree SHAP for trees (exact); kernel SHAP for any model (approximate). (4) **Best practice:** Use tree importance for a quick view; permutation or SHAP for interpretation and validation. If two features are correlated, importance may be split; consider grouping or domain knowledge.

---

### Q7.4 How decision tree works

**Source:** BalanceHero, Wipro

**Answer:** Recursively split the data by a feature and threshold that maximize information gain (or minimize impurity). Stop when max depth, min samples, or pure node. Prediction: follow path from root to leaf; output majority class (classification) or mean (regression). Prone to overfitting; control with max_depth, min_samples_leaf, pruning.

**Elaboration:** (1) **Split criterion:** Maximize information gain = parent_impurity - weighted sum of child impurities. For classification: Gini or entropy; for regression: MSE reduction. (2) **Greedy:** At each node we choose the best feature and threshold; no backtracking. (3) **Stopping:** Max depth, min samples per leaf, or when node is pure (impurity = 0). (4) **Overfitting:** Deep trees fit noise; use pruning (e.g. cost-complexity), max_depth, min_samples_leaf, or ensemble (RF, GBM). (5) **Interpretability:** Tree structure is human-readable; feature importance from splits; can extract rules.

---

<a id="8-clustering-dimensionality-reduction"></a>
## 8. Clustering & Dimensionality Reduction

### Q8.1 K-means – what we need to provide; hierarchical vs K-means

**Source:** BalanceHero

**Structured answer:**
1. **What:** K-means partitions n points into K clusters by minimizing within-cluster sum of squares. We need K, (optional) initial centroids, and distance metric (usually Euclidean). Hierarchical builds a dendrogram by merging/splitting clusters; no K upfront.
2. **Why:** K-means for fast, scalable partitioning when K is known and clusters are roughly spherical. Hierarchical when K is unknown or we want a hierarchy.
3. **How:** K-means: init centroids (e.g. k-means++) → assign each point to nearest centroid → recompute centroids → repeat. Hierarchical: start with n clusters → merge closest (by linkage) until one cluster; cut dendrogram for K.
4. **Challenges solved:** Unsupervised grouping; K-means scales to large n; hierarchical gives hierarchy and does not require K.
5. **Pros and cons:** K-means: Pros: Fast, scalable. Cons: Needs K; convex clusters; sensitive to init. Hierarchical: Pros: No K; hierarchy; flexible shapes with right linkage. Cons: O(n²) or more; does not scale as well.
6. **Difference from alternatives:** K-means vs hierarchical: K-means is flat and fast; hierarchical is tree and flexible. K-means vs DBSCAN: DBSCAN finds arbitrary shapes and noise, no K.
7. **Most common errors:** Wrong K; bad init (use k-means++); using Euclidean for non-spherical data; ignoring scale (normalize features); single link chaining in hierarchical.

**Answer:** **K-means needs:** K (number of clusters), initial centroids (or let algorithm init), distance metric (usually Euclidean). **Hierarchical:** No K upfront; build dendrogram; cut at height to get clusters. **When hierarchical over K-means:** When you want hierarchy, non-convex shapes (with right linkage), or don’t know K; K-means is faster and scales better.

---

### Q8.2 DBSCAN

**Source:** BalanceHero, Wipro list

**Answer:** Density-based: clusters are dense regions. **Parameters:** eps (neighborhood radius), min_samples (core point threshold). Core points have ≥ min_samples in eps; border points are in neighborhood of core; noise otherwise. **Pros:** No need to specify K; finds arbitrary shapes; identifies outliers. **Cons:** Sensitive to eps and min_samples.

**Elaboration:** (1) **Core point:** Has at least min_samples points within distance eps (including itself). (2) **Border point:** Not core but within eps of a core point; belongs to that cluster. (3) **Noise:** Neither core nor border. (4) **Clustering:** Form connected components of core points (two core points in same cluster if one is in the other's eps-neighborhood, transitively). Add border points to a neighboring cluster. (5) **Choosing eps:** Use k-distance plot (distance to k-th neighbor); look for "knee." (6) **Pros:** No K; arbitrary shapes; finds outliers. **Cons:** Struggles with varying density; eps/min_samples critical.

---

### Q8.3 t-SNE – principle and characteristics

**Source:** BalanceHero

**Answer:** **Principle:** Embed high-dim points so that pairwise similarities (Gaussian in high-dim, Student-t in low-dim) are preserved. Minimize divergence between distributions. **Characteristics:** Non-linear; good for visualization; perplexity controls neighborhood size; non-deterministic; not for feature reduction for downstream ML (use UMAP or PCA for that). Good for 2D/3D visualization.

**Elaboration:** (1) **Objective:** Preserve pairwise similarities. In high-dim use Gaussian kernel for similarity; in low-dim use heavy-tailed Student-t (so that moderate distances don't dominate). Minimize KL divergence between the two distributions. (2) **Perplexity:** Roughly the number of neighbors; typical 5–50. Low = focus on very local structure; high = more global. (3) **Non-deterministic:** Random init; run multiple times or fix seed. (4) **Not for feature reduction:** t-SNE has no natural out-of-sample mapping; use PCA or UMAP if you need to project new points. (5) **Crowding problem:** In 2D, many points want to be "moderately" far; Student-t relieves this and keeps clusters separated.

---

### Q8.4 PCA vs t-SNE vs UMAP

**Source:** Wipro list

**Answer:** **PCA:** Linear; preserves global variance; fast; interpretable (loadings). **t-SNE:** Non-linear; preserves local structure; good for viz; slow; no out-of-sample by default. **UMAP:** Non-linear; preserves local and more global structure; faster than t-SNE; can project new points. Use PCA for decorrelation/speed; t-SNE for 2D viz; UMAP for viz or low-dim features.

**Elaboration:** (1) **PCA:** Linear projection that maximizes variance (or minimizes reconstruction error). Eigenvectors of covariance matrix; fast O(min(n,d)³); interpretable loadings; good for decorrelation and as first step. Cannot capture non-linear structure. (2) **t-SNE:** Non-linear; preserves local structure; great for 2D viz; slow; no out-of-sample; run different each time. (3) **UMAP:** Non-linear; preserves local and more global structure than t-SNE; faster; has transform so you can project new points; good for viz and as input to downstream ML. (4) **When to use:** PCA for speed and interpretability; t-SNE for publication-quality 2D plots; UMAP when you need both viz and a low-dim representation for models.

---

<a id="9-deep-learning-transformers"></a>
## 9. Deep Learning & Transformers

### Q9.1 What is a Transformer?

**Source:** Real, Wipro

**Structured answer:**
1. **What:** A Transformer is a neural architecture based on self-attention (no recurrence), with encoder stacks (self-attention + FFN), optional decoder (with cross-attention), and positional encoding.
2. **Why:** Enables parallelization over sequence length and captures long-range dependencies in one step, unlike RNNs; scales well with data and compute.
3. **How:** Input + positional encoding → layers of multi-head self-attention (Q,K,V) and FFN with residual + layer norm; decoder adds cross-attention to encoder output; output head for task.
4. **Challenges solved:** Long-range dependency (attention over all positions); training speed (parallel); scalability (BERT, GPT, T5).
5. **Pros and cons:** Pros: Parallel, long context, scalable, state-of-the-art. Cons: O(n²) attention cost in sequence length; large data and compute needed.
6. **Difference from alternatives:** Versus RNN/LSTM: no recurrence, parallel, better long-range. Versus CNN: global attention vs local convolution. Encoder-only (BERT) vs decoder-only (GPT) vs encoder-decoder (T5).
7. **Most common errors:** Wrong positional encoding or forgetting it; attention mask bugs (e.g. causal); numerical instability without layer norm; too small model or data for the task.

**Answer:** The **Transformer** is an architecture that relies entirely on **self-attention** (and no recurrence). **Encoder:** Stack of layers; each layer has (1) multi-head self-attention (each token attends to all tokens in the sequence), (2) feed-forward network (FFN), with residual connections and layer normalization. **Decoder:** Similar, plus a **cross-attention** block where decoder tokens attend to the encoder output. **Positional encoding** (sinusoidal or learned) is added to inputs so the model knows token order. **Why it matters:** (1) **Parallelization:** Unlike RNNs, all positions can be computed in parallel. (2) **Long-range dependencies:** Attention can connect any two positions in one step. (3) **Basis for LLMs:** BERT (encoder-only), GPT (decoder-only), T5 (encoder-decoder).

**Elaboration:** (1) **Self-attention:** Each token produces Query, Key, Value; attention weights = softmax(QK^T / √d_k); output = weighted sum of V. So each position gets a mixture of information from all positions. (2) **Multi-head:** Multiple attention heads in parallel allow the model to attend to different types of relations (syntax, semantics, etc.). (3) **Layer norm** is applied before (pre-norm) or after (post-norm) sublayers; pre-norm is more common in modern models for training stability. (4) **Scale:** Transformers scale with data and parameters; they benefit from large compute and large datasets.

---

### Q9.2 Self-attention (query, key, value) and multi-head attention

**Source:** Wipro list

**Answer:** For each position: **Query** Q, **Key** K, **Value** V (linear projections of input). Attention weights: softmax(QK^T / √d_k); output = weighted sum of V. **Multi-head:** Multiple Q,K,V projections in parallel; concatenate and project. Captures different types of relationships (syntax, semantics, etc.).

**Elaboration:** (1) **Scaled dot-product:** Attention = softmax(QK^T / √d_k) V. The scale √d_k prevents dot products from growing large (which would make softmax saturated and gradients tiny). (2) **Q, K, V:** Each position gets three vectors (from linear projections of the input); Q = "what am I looking for," K = "what do I offer," V = "what I pass on." (3) **Multi-head:** h separate Q,K,V projections; we get h attention outputs, concatenate, then project. Allows the model to attend to different aspects (e.g. syntax vs semantics) in parallel. (4) **Masking:** In decoder, causal mask zeros out future positions so we only attend to past and present.

---

### Q9.3 Vanishing/exploding gradients – detection and mitigation

**Source:** Wipro, Zzazz

**Answer:** **Vanishing:** Gradients become very small in deep nets (saturating activations, long chains). **Exploding:** Gradients grow. **Mitigation:** ReLU/GLU activations; batch/layer norm; residual connections; careful init (Xavier/He); gradient clipping; smaller learning rates. **Detection:** Monitor gradient norms per layer during training.

**Elaboration:** (1) **Vanishing:** In deep nets, gradients are multiplied through layers; sigmoid/tanh saturate (gradient → 0), so gradients shrink exponentially. Fix: ReLU (gradient 0 or 1), residual connections (gradient can flow through identity), careful init (Xavier/He), layer norm. (2) **Exploding:** Weights or activations grow; gradients explode. Fix: gradient clipping (by norm or value), smaller LR, batch/layer norm, better init. (3) **Detection:** Log gradient norms per layer; if they decay to near zero (vanishing) or spike (exploding), adjust architecture or training. (4) **Residual:** Skip connection adds input to output so ∂L/∂input gets a +1 path; helps gradient flow in very deep nets.

---

### Q9.4 Batch vs Layer vs Instance normalization

**Source:** Wipro list

**Answer:** **Batch norm:** Normalize over batch dimension (and spatial for CNN); depends on batch size; used in CNNs. **Layer norm:** Normalize over features for each sample; no batch dependency; used in Transformers. **Instance norm:** Normalize over spatial for each channel/sample; used in style transfer. **When:** BN for CNNs with large batches; LN for RNNs/Transformers/small batches.

**Elaboration:** (1) **Batch norm:** Normalize across batch (and spatial dims in CNN); mean and variance are batch statistics. At test time use running average. Problem: depends on batch size; small batch → noisy stats; doesn't work well with RNNs (variable length) or with batch size 1. (2) **Layer norm:** Normalize across the feature dimension for each sample independently; no dependency on batch. Same at train and test. Used in Transformers and RNNs. (3) **Instance norm:** Normalize across spatial dimensions for each channel and each sample; removes instance-specific style; used in style transfer. (4) **Group norm:** Between BN and LN; normalize over a group of channels; useful when batch size is small.

---

### Q9.5 SGD vs Adam vs AdamW

**Source:** Wipro list

**Answer:** **SGD:** Plain gradient descent; can generalize well with tuning; needs momentum and LR schedule for deep nets. **Adam:** Adaptive LR per parameter (momentum + second moment); fast convergence; can overfit. **AdamW:** Adam with decoupled weight decay (correct L2 reg). **When:** SGD (with momentum) for full convergence and generalization; Adam/AdamW for faster iteration and Transformers.

**Elaboration:** (1) **SGD:** θ = θ - η∇L; simple but can be slow; momentum (v = μv + ∇L, θ -= ηv) helps. Often generalizes better with enough tuning and LR schedule. (2) **Adam:** Maintains per-parameter adaptive LR (first and second moment of gradients); fast convergence; can overfit compared to SGD in some settings. (3) **AdamW:** In Adam, L2 penalty in the loss is not equivalent to weight decay (due to adaptive LR). AdamW decouples weight decay: apply decay after the gradient update. Preferred for Transformers. (4) **When:** SGD+momentum for CNNs when training long and seeking best generalization; Adam/AdamW for Transformers and when you want fast iteration.

---

### Q9.6 Dropout – training vs inference; why it prevents overfitting

**Source:** Wipro list

**Answer:** **Training:** Randomly zero some activations with probability p. **Inference:** No dropout; often scale activations by 1-p so expected magnitude matches. Prevents overfitting by preventing co-adaptation of neurons and acting as ensemble of sub-networks.

**Elaboration:** (1) **Co-adaptation:** Without dropout, neurons can rely on specific other neurons; dropout forces each unit to be useful on its own or with a random subset, improving robustness. (2) **Ensemble view:** Each training step uses a "thinned" network; at test time we approximate the geometric mean of all thinned networks by scaling activations by (1-p) so the expected activation matches training. (3) **Where to apply:** Usually on hidden layers; sometimes on attention weights. (4) **Rate:** Typical p = 0.1–0.5; too high can underfit. (5) **Spatial dropout:** For conv layers, drop entire feature maps (channels) instead of individual elements to respect spatial structure.

---

### Q9.7 VAE – initialization and reconstruction loss in PyTorch

**Source:** BalanceHero

**Answer:** **Init:** Common: Xavier/Kaiming for linear layers; small init for log_var head so KL doesn’t dominate early. **Reconstruction loss:** For continuous data, MSE or BCE; for discrete, cross-entropy. **Total:** reconstruction + β * KL(q(z|x) || p(z)). Reparameterization: z = μ + σ*ε, ε ~ N(0,1). Example:

```python
def vae_loss(recon_x, x, mu, logvar):
    recon = F.mse_loss(recon_x, x, reduction='sum')  # or BCE
    kl = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon + kl
```

**Elaboration:** (1) **Reparameterization:** z = μ + σ·ε with ε ~ N(0,1) so we can backprop through the sampler; without it, sampling is non-differentiable. (2) **KL term:** -0.5 * sum(1 + log(σ²) - μ² - σ²) is the closed form of KL(q(z|x) || N(0,1)) for diagonal Gaussian q. (3) **Init log_var:** Initialize the layer that outputs log(σ²) to small negative values so σ is small initially; then the latent is close to μ and reconstruction dominates early; avoids posterior collapse. (4) **β-VAE:** Weight KL by β > 1 to encourage disentanglement; balance with reconstruction. (5) **Reconstruction:** MSE for continuous; BCE for binary; cross-entropy for discrete (e.g. tokens).

---

<a id="10-llm-rag-gen-ai"></a>
## 10. LLM, RAG & Gen AI

### Q10.1 RAG – what it is; where is DB, how stored

**Source:** Google, Wipro

**Structured answer:**
1. **What:** RAG = Retrieve relevant documents/chunks given a query, then augment the LLM prompt with that context and generate an answer. The "DB" is typically a vector store holding embeddings of chunks + metadata.
2. **Why:** Grounds LLM answers in your data, reduces hallucination, and allows up-to-date knowledge without retraining the model.
3. **How:** Chunk documents → embed with an embedding model → store in vector DB; at query time embed query → k-NN/ANN search → retrieve top-k chunks → build prompt (context + query) → call LLM → return answer.
4. **Challenges solved:** Hallucination (grounding in docs); knowledge cut-off (use your corpus); scale (retrieve only relevant parts instead of feeding everything).
5. **Pros and cons:** Pros: Fewer hallucinations; no retraining for new docs; interpretable (sources). Cons: Retrieval quality limits answer quality; latency (embed + search + LLM); chunking and embedding design matter.
6. **Difference from alternatives:** Versus fine-tuning: RAG adds knowledge without weight updates; easier to update docs. Versus pure LLM: RAG uses external store; pure LLM relies only on pretrained knowledge. Versus keyword search: RAG uses semantic (vector) similarity.
7. **Most common errors:** Bad chunking (too big/small, wrong boundaries); weak embedding model; no hybrid (keyword + vector); not evaluating retrieval separately; ignoring context length limits.

**Answer:** **RAG (Retrieval-Augmented Generation):** (1) **Retrieve:** Given a user query, find the most relevant pieces of information (chunks) from a corpus. (2) **Augment:** Pass those chunks as context (along with the query) to an LLM. (3) **Generate:** The LLM produces an answer conditioned on the retrieved context, reducing hallucination and grounding answers in your data. **Where is the DB?** The "database" is typically a **vector store** (e.g. Pinecone, Milvus, Chroma, Weaviate, Qdrant). **How stored:** Documents are split into chunks (by paragraph, fixed size, or semantic); each chunk is passed through an **embedding model** (e.g. sentence-transformers, OpenAI embeddings) to get a vector; vectors and optional metadata (source, title) are indexed in the vector DB. At query time: embed the query → run **k-NN or ANN search** → retrieve top-k chunks → construct a prompt with context + query → call LLM → return response.

**Elaboration:** (1) **Why vector DB?** Similarity search over raw vectors is O(n); vector DBs use approximate indexes (HNSW, IVF) for sublinear search. (2) **Why chunk?** LLMs have context limits; chunking keeps units small enough and allows precise retrieval. (3) **Hybrid search:** Combine vector similarity with keyword (BM25) or metadata filters for better recall. (4) **Evaluation:** Measure retrieval quality (recall@k, MRR) and end-to-end answer quality (faithfulness, relevance) with human or model-as-judge.

---

### Q10.2 Chunking strategies for RAG with examples

**Source:** Wipro

**Answer:** (1) **Fixed size:** e.g. 512 tokens with overlap; simple, may split sentences. (2) **Sentence/paragraph:** Split on sentence or paragraph boundaries; preserves coherence. (3) **Recursive character/semantic:** Split by separators (e.g. \n\n, \n, space) recursively to target size. (4) **Semantic:** Use embeddings or model to split at “topic” boundaries. (5) **Document-specific:** Tables, slides – chunk by structure. Example: “We use 256-token chunks with 50-token overlap and recursive splitting by paragraph then sentence.”

---

### Q10.3 Word2Vec vs BERT embeddings

**Source:** Wipro

**Answer:** **Word2Vec:** Static embeddings per word (CBOW/skip-gram); same vector for same word; no context. **BERT:** Contextual embeddings; same word gets different vectors in different sentences (encoder output). **RAG:** BERT-like (sentence-transformers) preferred for semantic similarity; Word2Vec for simple word similarity or legacy systems.

**Elaboration:** (1) **Word2Vec (CBOW/skip-gram):** Learns one fixed vector per word from local context; "bank" has one vector regardless of "river bank" vs "savings bank." Fast; good for word similarity and analogy. (2) **BERT (and sentence-transformers):** Contextual: the same word gets different vectors in different sentences (encoder output, often [CLS] or mean of tokens). Captures polysemy and sentence-level meaning. (3) **For RAG:** We compare query to chunk; sentence meaning matters more than word identity, so BERT-like embeddings (e.g. all-MiniLM, sentence-t5) are standard. (4) **Size:** Word2Vec typically 100–300 dim; BERT 768 or 384 (with pooling). (5) **Speed:** Word2Vec is faster to compute; BERT better quality for semantic search.

---

### Q10.4 Vector DB (e.g. Milvus) – architecture, working, monitoring, challenges

**Source:** Wipro

**Answer:** **Architecture:** Store vectors and metadata; build index (HNSW, IVF_FLAT, etc.); serve ANN search. **Working:** Insert vectors + metadata; index built in background; query returns k-NN by vector similarity and optional metadata filter. **Monitoring:** Latency, throughput, index size, recall@k, error rate. **Challenges:** Embedding drift, scale (sharding), consistency, cost of re-embedding.

**Elaboration:** (1) **Architecture:** Write path: ingest vectors + metadata → build/update index (HNSW, IVF, etc.) → serve. Read path: embed query → ANN search → return k-NN + metadata. (2) **Index types:** HNSW (graph, good recall/speed); IVF (quantize into buckets, search few buckets); hybrid with scalar index for filtering. (3) **Monitoring:** Latency (p50, p99), throughput (QPS), index size, recall@k (vs exact search), error rate. (4) **Challenges:** Embedding model change or corpus change → re-embed; scale → shard by vector or metadata; consistency → eventual vs strong; cost of re-embedding large corpora. (5) **Milvus:** Open-source; supports multiple index types; scaling and filtering; good for production at scale.

---

### Q10.5 Text completion vs conversational API

**Source:** Google

**Answer:** **Completion API:** Single prompt → single response; stateless; good for short Q&A, summarization. **Conversational API:** Multi-turn; state (chat history) maintained; good for assistants. Implementation: either send full history each time (stateless server) or maintain session and pass messages list (e.g. OpenAI chat completions with messages array).

**Elaboration:** (1) **Completion API:** Single prompt string; model returns one completion. Stateless; good for summarization, one-shot Q&A, code completion. No built-in notion of "conversation." (2) **Conversational (chat):** messages = [{role: "user"|"assistant"|"system", content: "..."}]. Model sees full thread; responds in character. Used for assistants and multi-turn. (3) **State:** Server can store session and append new user message + previous messages, or client sends full history each time (stateless server, simpler). (4) **Context window:** Long conversations can exceed context; use summarization, sliding window, or RAG to keep relevant history.

---

### Q10.6 Intent classification, function calling, tool use in OpenAI

**Source:** Google

**Answer:** **Intent classification:** Classify user intent (e.g. book_flight, cancel) with a small classifier or LLM. **Function/tool calling:** Define tools (name, description, parameters schema); model returns tool_calls (function name + arguments); application executes and returns result; optionally send back to model for final answer. Used for agents, structured actions, RAG (e.g. search tool).

**Elaboration:** (1) **Intent classification:** Can be a small classifier (e.g. BERT fine-tuned on intents) or an LLM call ("classify intent: ..."). Output: intent label + optional entities. (2) **Function/tool calling:** In the API you pass tools = [{type: "function", function: {name, description, parameters: JSON schema}}]. Model can return tool_calls = [{id, name, arguments: JSON}]. Your app runs the function and can pass the result back; model may then produce a final user-facing answer. (3) **Use cases:** Agents (search, calculator, DB query); RAG (tool = search_docs); booking (tool = check_availability). (4) **Best practices:** Clear tool descriptions; validate and sanitize arguments; handle errors and timeouts; idempotency for state-changing tools.

---

### Q10.7 How would an LLM know if the user is signing up again after 30 days (memory)?

**Source:** Google (links: LangMem, OpenAI agents lifecycle)

**Answer:** **Short-term:** Conversation window (recent messages in context). **Long-term:** External memory store: (1) **User-level store:** key-value or vector store keyed by user_id; store facts, events, preferences. (2) **Retrieval:** On each turn, retrieve relevant memories (e.g. by embedding or key) and inject into prompt. (3) **Update:** After each turn, extract and write new facts (e.g. “signed up on X”). So “signed up again after 30 days” is either in retrieved memory or computed from stored events (last_signup_date, current_date). Products: LangMem, OpenAI memory API, or custom store (Redis, DB, vector DB).

---

### Q10.8 Agentic evaluation – correct tool, call accuracy

**Source:** Google

**Answer:** For agent systems: (1) **Tool choice accuracy:** Did the agent pick the right tool for the step? (2) **Tool call accuracy:** Were arguments correct (exact match or semantic)? (3) **End-to-end:** Did the final answer match the gold answer? Metrics: precision/recall of tool calls; success rate on benchmark tasks; human eval on multi-step tasks.

---

### Q10.9 ReAct vs Plan-and-Execute vs Reflection agent patterns

**Source:** Wipro list

**Answer:** **ReAct:** Interleave reasoning (thought) and action (tool call) in a loop. **Plan-and-Execute:** First plan (sequence of steps), then execute steps (possibly with tools). **Reflection:** After an answer, generate critique and refine. **Use cases:** ReAct for flexible, reactive tasks; Plan-and-Execute for complex multi-step; Reflection when quality is critical and you can afford extra steps.

---

### Q10.10 Guardrails and safety for autonomous agents

**Source:** Wipro list

**Answer:** Input/output filters (e.g. block PII, harmful content); allowed-tool allowlist; timeouts and max steps; human-in-the-loop for sensitive actions; audit logs; rate limits; fallback to “I can’t do that” when unsure. Use frameworks like Guardrails AI, NeMo Guardrails, or custom validation.

---

### Q10.11 Context window limitations – strategies beyond truncation

**Source:** Wipro list

**Answer:** (1) **Summarization:** Summarize old context and keep summary + recent. (2) **Sliding window:** Keep only last N tokens. (3) **RAG:** Retrieve relevant chunks instead of full doc. (4) **Hierarchical:** Summarize sections, then summarize summaries. (5) **Long-context models:** Use models with larger windows when needed. (6) **Chunked processing:** Process in chunks and aggregate (e.g. map-reduce summarization).

---

### Q10.12 Compare Pinecone, Weaviate, Qdrant, ChromaDB

**Source:** Wipro list

**Answer:** **Pinecone:** Managed, scalable; good for production; paid. **Weaviate:** Open-source; graph + vector; hybrid search. **Qdrant:** Open-source; filtering, payload; Rust. **ChromaDB:** Lightweight; good for dev/prototype; simpler. **Choice factors:** Scale, latency, filtering needs, self-hosted vs managed, cost, ecosystem.

---

### Q10.13 Embedding drift – when to re-embed

**Source:** Wipro list

**Answer:** **Drift:** Query distribution or document corpus changes so that current embeddings no longer align. **When to re-embed:** (1) Major corpus update. (2) Change of embedding model. (3) Monitoring shows drop in retrieval quality (e.g. relevance, downstream task metric). (4) Scheduled (e.g. monthly) for critical indices. Re-embed incrementally if possible (new docs only) to save cost.

---

### Q10.14 Instruction tuning vs fine-tuning

**Source:** Wipro list

**Answer:** **Fine-tuning:** Update model weights on task-specific data (e.g. classification, NER). **Instruction tuning:** Train on (instruction, response) pairs so the model follows instructions and generalizes to new tasks. **When:** Fine-tuning when you have a clear task and enough data; instruction tuning for general “follow instructions” and zero-shot behavior. Trade-offs: instruction tuning is more general; fine-tuning can be more accurate for one task.

---

<a id="11-mlops-production-feature-store"></a>
## 11. MLOps, Production & Feature Store

### Q11.1 Demand forecasting – metrics to measure performance

**Source:** Zzazz, Zalando

**Answer:** **Point forecasts:** MAE, RMSE, MAPE, sMAPE. **Probabilistic:** Pinball loss (quantile), CRPS. **Bias:** Mean Error. **Business:** Stock-out rate, overstock cost. **Horizon:** Evaluate per horizon (e.g. 1-day, 7-day). Use backtesting and hold-out periods.

**Elaboration:** (1) **Point metrics:** MAE (mean absolute error), RMSE (penalizes large errors more), MAPE (percentage; be careful with near-zero actuals), sMAPE (symmetric). (2) **Probabilistic:** Pinball loss for quantile forecasts; CRPS (continuous ranked probability score) for full distribution. (3) **Bias:** Mean error (forecast - actual); positive = over-forecast. (4) **Business:** Stock-out rate (demand > supply); overstock cost; fill rate. (5) **Horizon:** Evaluate per step (1-day, 7-day, etc.); often accuracy degrades with horizon. (6) **Backtesting:** Rolling or expanding window; compare models on same periods. Hold out a final period for unbiased test.

---

### Q11.2 ARIMA modeling (brief)

**Source:** Zalando

**Answer:** ARIMA(p,d,q): AutoRegressive (p), Integrated (differencing, d), Moving Average (q). For stationary series (after differencing). Fit: estimate p,d,q (e.g. ACF/PACF or auto_arima); estimate coefficients; forecast. Good for univariate, short-horizon, when linear and stationary. Not for strong seasonality without SARIMA or for multivariate without VAR.

**Elaboration:** (1) **AR(p):** y_t depends on previous p values. (2) **I(d):** Differencing d times to make series stationary (remove trend). (3) **MA(q):** y_t depends on previous q errors. (4) **Identification:** Use ACF/PACF or auto_arima to choose p,d,q. (5) **SARIMA:** Adds seasonal terms (P,D,Q,s) for seasonal patterns. (6) **Limitations:** Linear; univariate; assumes stationary after differencing. For long-horizon or complex patterns, consider ML (e.g. Prophet, neural nets) or hybrid.

---

### Q11.3 Dynamic pricing – how did you monitor; degradation; scaling pipeline

**Source:** Zzazz

**Answer:** **Monitoring:** Track price recommendations vs actual prices; revenue and margin; conversion; model inputs (demand, competitor prices). **Degradation:** Monitor model metrics (accuracy, calibration); A/B test new model; rollback if KPIs drop. **Scaling pipeline:** Async job queue (e.g. Celery, K8s Jobs); batch inference; cache frequent segments; scale workers with load.

**Elaboration:** (1) **Monitoring:** Track recommended vs applied price; revenue and margin by segment; conversion and volume; model inputs (demand forecast, competitor prices, inventory). Alert on drift or anomalies. (2) **Degradation:** A/B test new model vs current; monitor accuracy (e.g. demand forecast error) and business KPIs; rollback if new model underperforms. Shadow mode (log new model output without applying) before full rollout. (3) **Scaling:** Async job queue (Celery, K8s Jobs) for batch scoring; cache prices for frequent segments; scale inference workers with load; consider real-time vs batch pipelines.

---

### Q11.4 Feature Store – why useful in ML workflows

**Source:** BalanceHero (real interview)

**Structured answer:**
1. **What:** A feature store is a central system for feature definitions, metadata, and (optionally) stored feature values (offline for training, online for serving).
2. **Why:** Single source of truth for features; same logic for training and serving (consistency); reuse across models; lineage and freshness control.
3. **How:** Define features (code or config); compute in batch or streaming; store in offline (e.g. table) and online (low-latency) stores; training and serving read from the store with point-in-time correctness where needed.
4. **Challenges solved:** Train–serve skew; duplicated feature logic; no lineage; slow feature availability at serve time.
5. **Pros and cons:** Pros: Consistency, reuse, lineage, optimized serving. Cons: Operational overhead; need to maintain and backfill; complexity for real-time vs batch.
6. **Difference from alternatives:** Versus ad-hoc pipelines: feature store enforces one definition and reuse. Versus no store: avoids skew and duplication. Feast vs Tecton vs cloud-native: open-source vs managed vs cloud DB–backed.
7. **Most common errors:** No point-in-time correctness (data leakage in training); inconsistent definitions between train and serve; not monitoring freshness or coverage; over-engineering for small teams.

**Answer:** A **feature store** is a central repository for feature definitions and (optionally) computed feature values. **Why useful:** (1) **Single source of truth:** One place for feature names, types, and logic; no drift between teams. (2) **Train–serve consistency:** The same transformation code and definitions are used in training and in serving, so the model sees the same feature space at inference. (3) **Reuse:** Multiple models can consume the same features; avoid recomputing in every pipeline. (4) **Lineage:** Track which jobs or data produced which feature tables; critical for debugging and compliance. (5) **Freshness:** Support both batch (historical, offline) and real-time (low-latency) feature computation; the store can serve the right view for training vs online inference. **Tools:** Feast (open-source), Tecton, Databricks Feature Store, SageMaker Feature Store, etc.

**Elaboration:** (1) **Without a feature store:** Ad-hoc scripts for training features and separate (often duplicated) logic in the serving service → inconsistency and bugs. (2) **Point-in-time correctness:** For training, we must not use "future" data; feature stores can support point-in-time joins so that at time t we only use features known at t. (3) **Online vs offline:** Offline store feeds training and batch scoring; online store serves low-latency features for real-time inference; they can be backed by the same definitions. (4) **Integration with MLflow:** Feature store + model registry + experiment tracking gives full lineage from raw data to deployed model.

---

### Q11.5 Training vs validation vs test; cross-validation

**Source:** BalanceHero

**Answer:** **Train set:** Used to fit the model (update weights). **Validation set:** Used to tune hyperparameters, choose the best model or checkpoint (early stopping), and compare architectures; not used for training. **Test set:** Used exactly once to report the final estimate of performance; must not influence any training or tuning decision (otherwise it is not an unbiased estimate). **Cross-validation (CV):** Split data into K folds; in turn, use one fold as validation and the rest as train; average the validation metric across folds. Gives a more stable estimate of performance and uses all data for validation over different splits. **Time-series:** Do not shuffle; use **expanding** (train on past, validate on next period) or **rolling** window (fixed-length train window) to avoid future information leaking into the past.

**Elaboration:** (1) **Why separate test?** If we use the same data for tuning and reporting, we overfit to that data and the reported metric is optimistic. (2) **Nested CV:** Outer loop for unbiased performance estimate, inner loop for model selection; expensive but correct. (3) **Stratified K-fold:** For classification, keep class proportions in each fold. (4) **Leave-one-out:** K = n; unbiased but high variance; use when data is very small.

---

### Q11.6 Feature selection – experience and methods

**Source:** BalanceHero, Wipro list

**Answer:** **Filter:** Correlation, mutual information, chi-square (no model). **Wrapper:** RFE, forward/backward selection (use model score). **Embedded:** L1 (Lasso), tree importance, in-model. **Experience:** Start with correlation + domain; then tree importance or permutation importance; validate on hold-out. Tableau: use built-in “Explain” or export and do selection in Python/R.

---

### Q11.7 Hyperparameter tuning – techniques

**Source:** BalanceHero

**Answer:** **Grid search:** Exhaustive over a grid. **Random search:** Sample from distributions. **Bayesian optimization:** Model the objective (e.g. Gaussian process); sample where improvement is likely. **Hyperband/BOHB:** Early stopping of bad configs to save time. **Tools:** Optuna, Ray Tune, SageMaker, MLflow + search.

**Elaboration:** (1) **Grid search:** Exhaustive over a discrete grid; simple but expensive; use for few critical params. (2) **Random search:** Sample from distributions; often finds good regions with fewer trials than grid. (3) **Bayesian optimization:** Model the objective (e.g. Gaussian process); acquisition function (EI, UCB) suggests next trial; sample-efficient. (4) **Hyperband/BOHB:** Run many configs for few iterations; keep best and run longer; early stopping saves cost. (5) **Multi-fidelity:** Cheap proxy (e.g. small subset, short training) to weed out bad configs; full evaluation only for promising ones.

---

### Q11.8 Evaluate model/product in production – hallucination, accuracy vs ground truth

**Source:** EY

**Answer:** **Accuracy vs ground truth:** When labels exist (e.g. delayed): log predictions and labels; compute accuracy/F1/MAE in batches. **Hallucination:** Use NLI model or LLM-as-judge to check factual consistency; sample and human eval; cite sources in RAG and check support. **In production:** A/B test; shadow mode; monitor input/output distributions and failure rates.

---

### Q11.9 Multi-data-type queries (audio, text, image) for chatbot

**Source:** EY

**Answer:** **Multimodal input:** Use multimodal model (e.g. GPT-4V, Whisper for audio) or separate encoders (image encoder + text encoder) and fuse (concat or cross-attention). **Pipeline:** Transcribe audio → text; embed image → vector; combine in one prompt or retrieval (e.g. image + text in same vector space). **Chatbot:** Single API that accepts text, image, or audio; route to appropriate encoder and then to LLM.

---

<a id="12-pyspark-large-scale-data"></a>
## 12. PySpark & Large-Scale Data

### Q12.1 Repartition vs coalesce vs repartitionByRange

**Source:** BalanceHero (real)

**Structured answer:**
1. **What:** Repartition(n) = full shuffle to n partitions (hash). Coalesce(n) = reduce to n partitions by merging (no full shuffle). RepartitionByRange(n, cols) = range partitioning on columns to n partitions.
2. **Why:** Repartition to increase parallelism or rebalance; coalesce to reduce partitions (e.g. before write) without shuffle cost; repartitionByRange for range queries and joins on the same key.
3. **How:** Repartition: hash partition → shuffle. Coalesce: combine existing partitions (e.g. 100→10); no shuffle. RepartitionByRange: sort/range partition on given columns.
4. **Challenges solved:** Skew reduction (repartition); fewer output files (coalesce); better join and range scan (repartitionByRange).
5. **Pros and cons:** Repartition: Pros: Even distribution. Cons: Full shuffle cost. Coalesce: Pros: No shuffle. Cons: Can leave skew. RepartitionByRange: Pros: Sorted partitions, join-friendly. Cons: Shuffle; can skew if key distribution is skewed.
6. **Difference from alternatives:** Repartition vs coalesce: repartition can increase or decrease with shuffle; coalesce only decreases without full shuffle. Hash vs range: hash spreads by key hash; range by key order.
7. **Most common errors:** Using repartition to reduce (expensive; use coalesce); coalesce to increase (no effect; use repartition); not tuning partition count (too many or too few); ignoring skew after coalesce.

**Answer:** **Repartition(n):** Triggers a **full shuffle**; data is redistributed so that the RDD/DataFrame has exactly n partitions. Uses **hash partitioning** (default) so keys are distributed across partitions. Use when you want to *increase* the number of partitions (e.g. for more parallelism) or when you need a more even distribution after filtering. **Coalesce(n):** **Reduces** the number of partitions by *merging* existing partitions (e.g. 100 → 10). Does **not** perform a full shuffle; it only combines partitions that are on the same executor where possible. Use when reducing partitions (e.g. before writing to fewer files) to avoid the cost of a shuffle. **RepartitionByRange(n, cols):** Partitions by **range** of the given columns; data is sorted by those columns across partitions. Good for range queries and for **joins on the same key** (both sides partitioned by the same key can avoid shuffle). **Summary:** Repartition = hash, full shuffle; Coalesce = merge, no full shuffle; RepartitionByRange = range, full shuffle but sorted.

**Elaboration:** (1) **When to use coalesce vs repartition for reduction:** Coalesce is cheaper (no shuffle) but can leave skewed partitions if data was uneven; repartition(n) gives even partitions but costs a shuffle. (2) **Skew:** After a filter, some partitions may be empty; coalesce can merge them. (3) **Writing:** Coalesce before write to avoid many small files (e.g. coalesce(1) or a small number for a single output file, though that can create a bottleneck). (4) **RepartitionByRange and sort:** In Spark 3, you can use repartitionByRange with a sort to get globally sorted data across partitions.

---

### Q12.2 PySpark performance tuning – factors and common practices

**Source:** BalanceHero

**Answer:** **Partitioning:** Right # of partitions (2–4 per core); avoid skew (salt key). **Caching:** cache()/persist() for reused DFs; unpersist when done. **Broadcast:** Small join side broadcast. **Predicate pushdown:** Filter early. **Avoid UDFs when possible:** Use built-in or Pandas UDF (vectorized). **Resource:** Executor memory, parallelism (spark.default.parallelism). **Shuffle:** Minimize; tune spark.sql.shuffle.partitions.

**Elaboration:** (1) **Partition count:** Aim for 2–4x number of cores; too many = overhead; too few = underutilization. After filter, coalesce to avoid many small tasks. (2) **Skew:** If one key dominates, that partition is slow. Salt the key (add random suffix) to spread load; then aggregate. (3) **Broadcast:** For small join dimension (< ~100MB), broadcast so no shuffle on that side. (4) **Predicate pushdown:** Filter and project early so less data flows through. (5) **UDFs:** Python UDFs are slow (serialization, GIL); use built-in or Pandas UDF (vectorized). (6) **spark.sql.shuffle.partitions:** Default 200; for large shuffles increase; for small reduce to avoid many small tasks.

---

<a id="13-software-engineering-fundamentals"></a>
## 13. Software Engineering Fundamentals

### Q13.1 What is a decorator (Python)

**Source:** Real

**Answer:** A function that takes a function and returns a new function (or callable). Used to add behavior (logging, retry, auth) without changing the original. Example:

```python
def retry(n=3):
    def dec(f):
        def wrap(*a, **k):
            for _ in range(n):
                try:
                    return f(*a, **k)
                except Exception:
                    pass
            raise
        return wrap
    return dec
```

**Elaboration:** (1) **Syntax:** @decorator above a function is equivalent to func = decorator(func). Decorators can take arguments: @retry(3) → func = retry(3)(func). (2) **Use cases:** Logging, timing, retry, auth check, caching (e.g. lru_cache), validation. (3) **Preserving metadata:** Use functools.wraps(func) inside the wrapper so __name__, __doc__ are preserved. (4) **Class decorators:** Same idea; decorator receives the class. (5) **In ML:** Use for retry on model load, logging inference latency, or rate limiting.

---

### Q13.2 Multi-threading (Python)

**Source:** Real

**Answer:** Threads share memory; GIL in CPython allows only one thread to run Python bytecode at a time, so CPU-bound work doesn’t parallelize. Use threads for I/O-bound work (e.g. concurrent requests). For CPU-bound, use multiprocessing. asyncio is an alternative for I/O-bound concurrency.

**Elaboration:** (1) **GIL (Global Interpreter Lock):** In CPython, one thread at a time executes Python bytecode. So CPU-bound threads (e.g. heavy computation) do not run in parallel; only one uses the CPU. (2) **I/O-bound:** When a thread waits on I/O (network, disk), it releases the GIL; other threads can run. So threads help for concurrent I/O (e.g. many HTTP requests). (3) **Multiprocessing:** Separate processes have separate GILs; true parallelism for CPU-bound work. (4) **asyncio:** Single-threaded cooperative multitasking; coroutines yield on I/O; good for many I/O-bound tasks without thread overhead. (5) **In ML:** Use threads for concurrent inference requests (I/O wait on GPU) or multiprocessing for data loading; avoid CPU-bound work in threads.

---

### Q13.3 SOLID principles

**Source:** Real

**Structured answer:**
1. **What:** S = single responsibility; O = open for extension, closed for modification; L = Liskov substitution (subtypes replaceable); I = interface segregation (small interfaces); D = dependency inversion (depend on abstractions).
2. **Why:** To design maintainable, testable, and extensible code; reduce coupling and ease change.
3. **How:** One class one job (S); use interfaces and composition to extend (O); ensure subtypes honor contracts (L); many specific interfaces over one fat interface (I); inject abstractions, not concretions (D).
4. **Challenges solved:** Monolithic classes; rigid design; untestable code; tight coupling.
5. **Pros and cons:** Pros: Clear structure; easier testing and evolution. Cons: More classes/interfaces; can be overkill for tiny projects.
6. **Difference from alternatives:** Versus "get it working": SOLID favors long-term maintainability. Dependency injection vs new inside: DI enables testing and swapping. Interfaces vs concrete classes: depend on interfaces for flexibility.
7. **Most common errors:** God classes (violate S); modifying core logic to add features (violate O); subtypes that break base contracts (violate L); fat interfaces (violate I); high-level module depending on low-level details (violate D).

**Answer:** **S – Single Responsibility:** A class/module should have one reason to change; one job. E.g. separate "load data," "preprocess," "train," "serve." **O – Open/Closed:** Open for extension (new behavior via new code) but closed for modification (don't change existing code). Use interfaces, strategy pattern, or plugins. **L – Liskov Substitution:** Subtypes must be substitutable for their base type without breaking correctness. If S is a subtype of T, any code that expects T should work with S. **I – Interface Segregation:** Many small, specific interfaces are better than one large one; clients shouldn't depend on methods they don't use. **D – Dependency Inversion:** Depend on abstractions (interfaces, abstract classes), not concretions. High-level modules shouldn't depend on low-level details; both should depend on abstractions.

**Elaboration:** **In ML systems:** (1) Single responsibility: separate data pipeline, training script, and inference server. (2) Open/closed: add new model types by implementing a Model interface rather than editing the training loop. (3) Liskov: any Model implementation can be swapped in the serving layer. (4) Interface segregation: don't force every model to implement "explain" if only some support it. (5) Dependency inversion: the serving API depends on ModelLoader interface, not on "load_sklearn" or "load_pytorch" directly; inject the concrete loader at runtime. This improves testability (mock the loader) and flexibility.

---

### Q13.4 Dependency injection

**Source:** Real

**Answer:** Dependencies (e.g. DB client, model loader) are passed in from outside rather than created inside the class. Enables testing (mock dependencies) and swapping implementations. In FastAPI: use `Depends()` to inject DB sessions, config, etc.

**Elaboration:** (1) **Why:** Classes that create their own dependencies are hard to test (you cannot easily replace the DB with a mock) and are tightly coupled. Injecting dependencies from outside (constructor or function args) allows swapping implementations. (2) **Testing:** Pass a mock or fake (e.g. in-memory DB) in tests; no need for real DB or API. (3) **FastAPI Depends():** Declare a function that returns the dependency (e.g. get_db() yields a session); the framework calls it per request and injects the result. (4) **In ML:** Inject ModelLoader, FeatureStore, or Config so that the serving code depends on abstractions; in production inject real implementations, in tests inject stubs.

---

<a id="14-behavioral-process"></a>
## 14. Behavioral & Process

### Q14.1 Why do you want to join [company]? What would colleagues say (positive/negative)? Nightmare manager? Challenges and how you resolved? Strengths and weaknesses?

**Source:** Zalando, various

**Answer:** Prepare 1–2 concrete stories (situation, task, action, result). For “colleagues”: positive (e.g. reliable, clear communicator); negative (e.g. sometimes too deep in details – and how you mitigate). Nightmare manager: e.g. micromanagement, no trust; flip to what you value (autonomy, clarity). Strengths: align with role (e.g. ownership, debugging). Weaknesses: real but improved (e.g. “I used to over-engineer; now I time-box design”).

---

### Q14.2 User-level access in Dockerfile

**Source:** Tata Digital (likely “how to run as non-root in Docker”)

**Answer:** Create a user in the Dockerfile and switch to it: `RUN adduser --disabled-password appuser` and `USER appuser`. Run the process as that user so the container doesn’t run as root (security best practice).

---

## Quick Reference: Coding Snippets Summary

| Topic | Key idea |
|-------|----------|
| Min strokes | Recursive: horizontal layer vs vertical; split at min height |
| Merge no extra space | Gap method (shell-sort style across two arrays) |
| m bouquets | Binary search on day; greedy count adjacent bloomed flowers |
| Jump game | Farthest reachable index |
| Longest substring no repeat | Sliding window + last index map |
| Equal 0s and 1s | Prefix sum 0 → -1; first occurrence of prefix sum |
| Next permutation | Find first increase from right; swap with next larger; reverse suffix |
| Missing number | n*(n+1)//2 - sum(arr) or XOR |
| Trie autocomplete | Insert; search prefix; DFS from node for completions |

---

---

## Structured answer template (use for any question)

For any question, answer in this order where applicable:

| # | Point | What to include |
|---|--------|------------------|
| 1 | **What** | Definition; what the concept/solution is in one or two sentences. |
| 2 | **Why** | Motivation; why we need it or why the approach is used. |
| 3 | **How** | Steps, algorithm, or mechanism; how it works in practice. |
| 4 | **Challenges solved** | What problems or limitations it addresses. |
| 5 | **Pros and cons** | Advantages and disadvantages; when it shines and when it does not. |
| 6 | **Difference from alternatives** | How it compares to other methods or technologies. |
| 7 | **Most common errors** | Typical pitfalls, bugs, or mistakes when using or implementing it. |

**Questions that already have a full "Structured answer" block:** Q1.1, Q1.4, Q1.7, Q2.1, Q2.5, Q3.1, Q4.1, Q5.2, Q6.1, Q6.2, Q6.6, Q6.7, Q7.1, Q7.2, Q8.1, Q9.1, Q10.1, Q11.4, Q12.1, Q13.3. For other questions, use the template above to fill in the same structure.

---

*Sources: Google, Tata Digital, Zzazz, Adobe, Zalando, BalanceHero, Wipro, Expedia, EY, and similar real interview reports. Use this doc alongside [INTERVIEW_PREP.md](./INTERVIEW_PREP.md) and the [ensemble project](./ensemble_project/) for end-to-end ML and coding prep.*
