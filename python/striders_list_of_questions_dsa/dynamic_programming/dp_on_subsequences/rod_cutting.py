def solve(ind:int, N:int, rod_len:list, val:list, dp:list[list])->int:
	if ind==0:
		return N/rod_len[ind]*val[ind]
	if dp[ind][N] != -1:
		return dp[ind][N]
	not_taken = solve(ind-1, N, rod_len, val, dp)
	taken = -int(1e9)
	if (rod_len[ind]<=N):
		taken = val[ind]+ solve(ind-1,N-rod_len[ind], rod_len, val, dp)
	dp[ind][N] = max(taken, not_taken)
	return max(taken, not_taken)

if __name__ == "__main__":
    price = [2,5,7,8,10]
    N = 5
    rod_len = range(1,N+1)
    dp = [[-1 for _ in range(N+1)] for _ in range(N)]
    print(solve(N-1, N, rod_len, price, dp))
