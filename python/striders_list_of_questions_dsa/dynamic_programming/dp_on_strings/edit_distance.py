def solve(i:int, j:int, s1:str, s2:str, dp:list[list]):
	if i<0:
		return j+1
	if j<0:
		return i+1
	if dp[i][j] != -1:
		return dp[i][j]
	if s1[i] == s2[j]:
		dp[i][j] = 0+ solve(i-1,j-1, s1, s2, dp)
	else:
		dp[i][j] = 1 + min(solve(i-1,j,s1,s2,dp), min(solve(i-1,j-1,s1,s2,dp), solve(i, j-1, s1,s2,dp)))
	return dp[i][j]


if __name__ == "__main__":
    s1 = "horse"
    s2 = "ros"
    n = len(s1)
    m = len(s2)
    dp = [[-1 for _ in range(m)] for _ in range(n)]
    print(solve(n-1, m-1, s1, s2, dp))
