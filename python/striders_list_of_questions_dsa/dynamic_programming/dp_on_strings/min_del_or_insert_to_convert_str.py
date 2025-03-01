def lcs(s1,s2):
    n = len(s1)
    m = len(s2)
    dp = [[-1 for _ in range(m+1)] for _ in range(n+1)]
    for i in range(n+1):
        dp[i][0] = 0
    for j in range(m+1):
        dp[0][j] =0

    for i in range(n+1):
        for j in range(m+1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = 1 + dp[i-1][j-1]
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[n][m]


if __name__ == "__main__":
    str1 = "abcd"
    str2 = "anc"
    n = len(str1)
    m = len(str2)
    k = lcs(str1,str2)
    print((n-k)+(m-k))
