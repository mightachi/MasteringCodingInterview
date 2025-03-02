def mcm(i,j,n,arr, dp):
	if i == j:
		return 0
	if dp[i][j]!= -1:
		return dp[i][j]
	mini = int(1e9)
	for k in range(i,j):
		ans = mcm(i,k,n,arr,dp) + mcm(k+1,j,n,arr,dp) + arr[i-1]*arr[k]*arr[j]
		mini =min(mini, ans)
		dp[i][j] = mini
	return mini

arr = [10, 20, 30, 40, 50]
n = len(arr)
dp = [[-1 for _ in range(n)] for _ in range(n)]
print(mcm(1,n-1,n,arr, dp))