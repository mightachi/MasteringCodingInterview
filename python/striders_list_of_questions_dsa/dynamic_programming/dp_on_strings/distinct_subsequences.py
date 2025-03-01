def solve(i, j, s1, s2, dp) -> int:
    if j<0:
        return 1
    if i<0:
        return 0
    
    if dp[i][j] != -1:
        return dp[i][j]
    if s1[i] == s2[j]:
        dp[i][j] = solve(i-1,j-1,s1,s2,dp) + solve(i-1,j,s1,s2,dp)
        return dp[i][j]
    else:
        dp[i][j] = solve(i-1,j,s1,s2,dp)
        return dp[i][j]


if __name__ == "__main__":
    s1 = "babgbag"
    s2 = "bag"
    n = len(s1)
    m = len(s2)
    dp = [[-1 for _ in range(m)] for _ in range(n)]
    print(solve(n-1, m-1, s1, s2, dp))

