def solve(ind:int, target: int, arr: list[list], dp: list[list]) -> bool:
	if target == 0:
		return True
	if ind == 0: 
		return arr[ind] == target
	if dp[ind][target] != -1:
		return dp[ind][target]
	not_taken= solve(ind-1, target, arr, dp)
	taken = False
	if arr[ind] <= target:
		taken = solve(ind-1, target-arr[ind], arr, dp)
	dp[ind][target] = not_taken or taken
	return not_taken or taken


if __name__ == "__main__":
    # arr = [1, 2, 3, 4]
    # Assuming the integer are positive and not negative
    arr = [-36,36]
    n = len(arr)

    total_sum = sum(arr)
    offset = total_sum  # Shift to handle negative targets
    dp = [[-1 for _ in range(2 * total_sum + 1)] for _ in range(n)]  # Adjust dp size
    for i in range(total_sum + 1):
        dummy = solve(n-1, i, arr, dp)  # Shift target by offset
    
    mini = float('inf')
    for i in range(total_sum + 1):
        if dp[n-1][i] == True:
            diff = abs(i - (total_sum - i))
            mini = min(mini, diff)
    print(mini)

