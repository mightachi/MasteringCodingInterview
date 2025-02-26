def solve(i:int, j:int, dp: list[list]) -> int:
    if i==0 and j==0:
        return 1
    if i<0 or j<0:
        return 0
    if dp[i][j] != -1:
        return dp[i][j]
    up = solve(i-1,j,dp)
    left = solve(i, j-1, dp)
    dp[i][j] = up + left
    return dp[i][j]

def tab_solve(m:int, n:int) -> int:
    dp = [[-1 for j in range(n)] for i in range(m)]
    dp[0][0] = 1

    for i in range(m):
        dp[i][0] = 1  # Only one way to reach any cell in the first column
    for j in range(n):
        dp[0][j] = 1 

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]

    return dp[m-1][n-1]


def so_solve(m:int, n:int):
	prev = [1 for _ in range(n)]
	for i in range(1,m):
		temp = [0]*n
		for j in range(n):
			up = prev[j]
			if j>0:
				left = temp[j-1]
			else:
				left = 0
			temp[j] = up+left
		prev = temp
	return prev[n-1]


if __name__ == "__main__":
    m=3
    n=2
    dp = [[-1 for j in range(n)] for i in range(m)]
    print(solve(m-1,n-1, dp))
    print(tab_solve(m,n))
    print(so_solve(m,n))

