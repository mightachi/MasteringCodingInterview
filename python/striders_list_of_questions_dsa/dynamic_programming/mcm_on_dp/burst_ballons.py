def burst_balloons(i,j,arr,dp):
	if i>j:
		return 0
	if dp[i][j] != -1:
		return dp[i][j]
	maxi = -int(1e9)
	for k in range(i,j+1):
		cost = burst_balloons(i,k-1,arr,dp) + burst_balloons(k+1,j,arr,dp) + arr[i-1]*arr[k]*arr[j+1]
		maxi = max(maxi, cost)
	dp[i][j] = maxi
	return dp[i][j]

a = [3, 1, 5, 8]
n = len(a)
dp = [[-1 for _ in range(n+1)] for _ in range(n+1)]
a = [1] + a + [1]
print(burst_balloons(1,n,a,dp))



