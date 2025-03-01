def solve(ind:int, target: int, arr: list[list], dp: list[list]) -> bool:
	if target ==0:
		return True
	if ind ==0:
		return arr[ind] == target
	if dp[ind][target] != -1:
		return dp[ind][target]
	not_taken = solve(ind-1, target, arr, dp)
	taken = False
	if arr[ind] <= target:
		taken = solve(ind-1, target-arr[ind], arr, dp)
	dp[ind][target] = not_taken or taken
	return dp[ind][target]


if __name__ == "__main__":
    # Test case 1 output: true
    arr = [2, 3, 3, 3, 4, 5]
    n = len(arr)
    
    total_sum = sum(arr)
    if total_sum % 2 != 0:
        print(False)
    else:
        target = total_sum//2
        dp = [[-1 for _ in range(target+1)] for _ in range(n)]
        print(solve(n-1, target, arr, dp))
