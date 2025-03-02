def mcm(arr):
	n = len(arr)
	dp = [[-1 for _ in range(n)] for _ in range(n)]
	for i in range(n):
		dp[i][i]=0

	for i in range(n-1,0,-1):
		for j in range(i+1,n):
			dp[i][j] = int(1e9)
			for k in range(i,j):
				cost = dp[i][k]+dp[k+1][j] + arr[i-1]*arr[k]*arr[j]
				dp[i][j] = min(dp[i][j],cost)
	return dp[i][j]

arr = [10, 20, 30, 40, 50]
print(mcm(arr))