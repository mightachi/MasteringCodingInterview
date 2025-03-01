def solve(ind:int, W:int, w:list, v:list, dp:list[list])-> int:
	if ind==0:
		return W/w[ind] * v[ind]
	if dp[ind][W] != -1:
		return dp[ind][W]
	not_taken = solve(ind-1, W, w, v, dp)
	taken = -int(1e9)
	if w[ind] <= W:
		taken = v[ind] + solve(ind, W-w[ind], w, v, dp)
	dp[ind][W] = max(taken, not_taken)
	return max(taken, not_taken)

if __name__ == "__main__":
    wt = [2, 4, 6]
    val = [5, 11, 13]
    W = 10
    n = len(wt)
    dp = [[-1 for _ in range(W+1)] for _ in range(n)]
    print(solve(n-1,W,wt,val,dp))