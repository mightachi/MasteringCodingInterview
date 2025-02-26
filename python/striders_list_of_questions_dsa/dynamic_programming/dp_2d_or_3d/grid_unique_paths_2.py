def solve(m, n, arr, dp):
    if m<0 or n<0 or arr[m][n] == -1:
        return 0
    if m==0 and n==0:
        return 1
    if dp[m][n]!=-1:
        return dp[m][n]

    up = solve(m-1, n, arr, dp)
    left = solve(m, n-1, arr, dp)
    dp[m][n] = up+left
    return dp[m][n]

def tab_solve(m, n, arr):
    dp = [[-1 for j in range(n)] for i in range(m)]
    for i in range(m):
        for j in range(n):
            if i<0 or j<0 or arr[i][j] == -1:
                dp[i][j] = 0
                continue
            if i==0 and j==0:
                dp[i][j] = 1
                continue
            
            up = 0
            left = 0
            if i>0:
                up = dp[i-1][j]
            if j>0:
                left = dp[i][j-1]
            dp[i][j] = up + left
    return dp[m-1][n-1]


def so_solve(m, n, arr):
    prev = [0] * n

    for i in range(m):
        temp = [0] * n
        for j in range(n):
            if i<0 or j<0 or arr[i][j]==-1:
                temp[j] = 0
                continue
            if i==0 and j==0:
                temp[j] = 1
                continue
            up = 0
            left = 0
            if i>0:
                up = prev[j]
            if j>0:
                left = temp[j-1]
            temp[j] = up + left
        prev = temp
    return prev[n-1]



if __name__ == "__main__":
    arr = [[0,0,0],[0,-1,0],[0,0,0]]
    
    m = 3
    n = 3
    dp = [[-1 for j in range(n)] for i in range(m)]
    print(solve(m-1,n-1, arr, dp))
    print(tab_solve(m,n, arr))
    print(so_solve(m,n, arr))