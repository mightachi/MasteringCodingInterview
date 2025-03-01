def solve(ind:int, target:int, arr: list, dp: list[list]) -> int:
	if ind==0:
		if target % arr[ind] == 0:
			return 1
		else:
			return 0
	if dp[ind][target] != -1:
		return dp[ind][target]
	not_take  = solve(ind-1, target, arr, dp)
	taken = 0
	if arr[ind]<=target:
		taken = solve(ind, target-arr[ind], arr, dp)
	dp[ind][target] = taken + not_take
	return taken + not_take

if __name__ == "__main__":
    arr = [1,2,3]
    target = 4
    n = len(arr)
    dp = [[-1 for _ in range(target +1)] for _ in range(n)]
    print(solve(n-1, target, arr, dp))