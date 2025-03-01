def solve(ind1:int, ind2:int, s1:str, s2:str, dp:list[list]) -> int:
	if ind1<0 or ind2<0:
		return 0
	if dp[ind1][ind2] != -1:
		return dp[ind1][ind2]
	if s1[ind1] == s2[ind2]:
		dp[ind1][ind2] = 1 + solve(ind1-1, ind2-1, s1,s2,dp)
		return dp[ind1][ind2]
	else:
		dp[ind1][ind2] = 0 + max(solve(ind1, ind2-1, s1,s2,dp), solve(ind1-1, ind2, s1, s2, dp))
		return dp[ind1][ind2]

def tab_solve(s1,s2,):
	n = len(s1)
	m = len(s2)
	dp = [[-1 for _ in range(m+1)] for _ in range(n+1)]
	
	for i in range(n+1):
		dp[i][0] = 0
	for j in range(m+1):
		dp[0][j] = 0
	for i in range(1, n+1):
		for j in range(1, m+1):
			if s1[i-1]==s2[j-1]:
				dp[i][j] = 1 + dp[i-1][j-1]
			else:
				dp[i][j] = max(dp[i-1][j], dp[i][j-1])
	return dp[n][m]



if __name__ == "__main__":
    s1 = "acd"
    s2 = "ced"
    n = len(s1)
    m = len(s2)
    dp = [[-1 for _ in range(m)] for _ in range(n)]
    print(solve(n-1,m-1,s1,s2,dp))
    print(tab_solve(s1,s2))