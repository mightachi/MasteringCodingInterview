def tab_solve(s1,s2):
	n = len(s1)
	m = len(s2)
	dp = [[-1 for _ in range(m+1)] for _ in range(n+1)]
	for i in range(n+1):
		dp[i][0] = 0
	for j in range(m+1):
		dp[0][j] = 0
	
	maxi = -int(1e9)
	for i in range(1, n+1):
		for j in range(1, m+1):
			if s1[i-1] == s2[j-1]:
				dp[i][j] = 1 + dp[i-1][j-1]
			else:
				dp[i][j] = 0
			maxi = max(dp[i][j], maxi)
	return maxi

if __name__ == "__main__":
    s1 = "abcjklp"
    s2 = "acjkp"
    print(tab_solve(s1,s2))