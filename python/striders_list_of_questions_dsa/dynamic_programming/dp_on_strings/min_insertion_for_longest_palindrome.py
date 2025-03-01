def tab_solve(s1,s2):
	n = len(s1)
	dp = [[-1 for _ in range(n+1)] for _ in range(n+1)]
	for i in range(n+1):
		dp[i][0] = 0
	for j in range(n+1):
		dp[0][j] = 0
	for i in range(1, n+1):
		for j in range(1, n+1):
			if s1[i-1] == s2[j-1]:
				dp[i][j] = 1 + dp[i-1][j-1]
			else:
				dp[i][j] = max(dp[i-1][j], dp[i][j-1])
	return dp[n][n]

if __name__ == "__main__":
    s = "abcaa"
    length = tab_solve(s, s[::-1])
    print(len(s)-length)