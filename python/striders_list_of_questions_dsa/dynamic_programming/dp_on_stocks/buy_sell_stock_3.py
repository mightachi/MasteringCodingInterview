def solve(ind, buy, cap, arr, dp) -> int:
	if ind==n or cap==0:
		return 0
	if dp[ind][buy][cap] != -1:
		return dp[ind][buy][cap]
	if buy == 0:
		op1 = solve(ind+1, buy, cap, arr, dp)
		op2 = -arr[ind] + solve(ind+1, 1, cap, arr, dp)
	elif buy == 1:
		op1 = solve(ind+1, buy, cap, arr, dp)
		op2 = arr[ind] + solve(ind+1, 0, cap-1, arr, dp)
	dp[ind][buy][cap] = max(op1, op2)
	return max(op1, op2)

if __name__ == "__main__":
    prices = [3, 3, 5, 0, 0, 3, 1, 4]
    n = len(prices)
    dp = [[[-1 for _ in range(3)] for _ in range(2)] for _ in range(n)]
    print(solve(0,0,2,prices,dp))