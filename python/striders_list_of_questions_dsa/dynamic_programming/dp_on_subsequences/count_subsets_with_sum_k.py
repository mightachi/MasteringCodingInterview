def solve(ind:int, target, arr:list, dp:list[list]) -> int:
	if target == 0:
		return 1
	if ind == 0:
		if arr[ind] == target:
			return 1
		else:
			return 0
	if dp[ind][target] != -1:
		return dp[ind][target]
	not_taken = solve(ind-1, target, arr, dp)
	taken = 0
	if arr[ind]<= target:
		taken = solve(ind-1, target - arr[ind], arr, dp)
	dp[ind][target] = taken + not_taken
	return taken + not_taken

def count_subsets_memo(arr, k):
    """
    Counts the number of subsets in 'arr' that sum up to 'k' using memoization.

    Args:
        arr: A list of positive integers.
        k: The target sum.

    Returns:
        The number of subsets with sum 'k'.
    """

    n = len(arr)
    memo = {}  # Use a dictionary for memoization

    def solve(index, target):
        if target == 0:
            return 1
        if index == 0:
            return 1 if arr[0] == target else 0

        if (index, target) in memo:
            return memo[(index, target)]

        not_taken = solve(index - 1, target)
        taken = 0
        if arr[index] <= target:
            taken = solve(index - 1, target - arr[index])

        memo[(index, target)] = not_taken + taken
        return memo[(index, target)]

    return solve(n - 1, k)



if __name__ == "__main__":
    arr = [1, 2, 2, 3] # output: 3
    k = 3
    arr = [28,4,3,27,0,24,26] # output: 2
    k = 24
    n = len(arr)
    dp = [[-1 for _ in range(k+1)] for _ in range(n)]
    print(solve(n-1, k, arr, dp))

    # Example usage:
    arr1 = [1, 2, 2, 3]
    k1 = 3
    print(f"Number of subsets for arr1 and k1: {count_subsets_memo(arr1, k1)}")  # Output: 3

    arr2 = [28, 4, 3, 27, 0, 24, 26]
    k2 = 24
    print(f"Number of subsets for arr2 and k2: {count_subsets_memo(arr2, k2)}") # Output: 2

    arr3 = [0,0,0,0,0,0,0,0,0,0]
    k3 = 0
    print(f"Number of subsets for arr3 and k3: {count_subsets_memo(arr3, k3)}") #Output: 1024