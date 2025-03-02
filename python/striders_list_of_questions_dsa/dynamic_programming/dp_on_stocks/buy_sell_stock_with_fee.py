def solve(ind,buy,fee,arr,dp):
	if ind==n:
		return 0
	if dp[ind][buy] != -1:
		return dp[ind][buy]
	if buy==0:
		op1 = solve(ind+1,buy,fee,arr,dp)
		op2 = -arr[ind] + solve(ind+1,1,fee,arr,dp)
	elif buy ==1:
		op1 = solve(ind+1,buy,fee,arr,dp)
		op2 = arr[ind]-fee+solve(ind+1, 0,fee,arr,dp)
	dp[ind][buy] = max(op1,op2)
	return max(op1,op2)

if __name__ == "__main__":
    prices = [1, 3, 2, 8, 4, 9]
    n = len(prices)
    fee = 2
    dp = [[-1 for _ in range(2)] for _ in range(n)]
    print(solve(0,0,fee,prices,dp))