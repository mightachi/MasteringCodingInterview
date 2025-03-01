def solve(i:int, j:int, s1, s2, dp)-> bool:
    if i<0 and j<0:
        return True
    if i<0 and j>=0:
        return False
    if j<0 and i>=0:
        isAllStars(s1,i)
    if dp[i][j] != -1:
        return dp[i][j]
    if s1[i] == s2[j] or s1[i] == "?":
        dp[i][j] = solve(i-1,j-1, s1,s2,dp)
        return dp[i][j]
    elif s1[i] == "*":
        dp[i][j] = solve(i-1,j,s1,s2,dp) or solve(i,j-1,s1,s2, dp)
        return dp[i][j]
    else:
        dp[i][j] = False
        return False

def isAllStars(s,i):
	while i>-1:
		if s[i] != "*":
			return False
	return True

if __name__ == "__main__":
    S1 = "ab*cd"
    S2 = "abdefcd"
    S1 = "ab?cd"
    S2 = "abdefcd"
    n = len(S1)
    m = len(S2)
    dp = [[-1 for _ in range(m)] for _ in range(n)]
    print(solve(n-1,m-1, S1,S2,dp))