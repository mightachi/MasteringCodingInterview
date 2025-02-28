def solve(i:int, j:int, m, arr, dp)-> int:
    if j<0 or j>=m:
        return float('-inf')

    if dp[i][j] != -1:
        return dp[i][j]
    if i==0:
        return arr[i][j]


    up = arr[i][j] + solve(i-1, j, m, arr, dp)
    left_diagonal = arr[i][j] + solve(i-1, j-1, m, arr, dp)
    right_diagonal = arr[i][j] + solve(i-1, j+1, m, arr, dp)

    dp[i][j] = max(up, max(left_diagonal, right_diagonal))
    return dp[i][j]

def tab_solve(n:int, m:int, arr:list[list]) -> int:
    dp = [[0 for j in range(m)] for i in range(n)]

    for j in range(m):
        dp[0][j] = arr[0][j]

    for i in range(1, n):
        for j in range(m):
            up = arr[i][j] + dp[i-1][j]
            left_diagonal = arr[i][j]
            if j-1>=0:
                left_diagonal += dp[i-1][j-1]
            else:
                left_diagonal += float('-inf')
            right_diagonal = arr[i][j]
            if j+1<m:
                right_diagonal += dp[i-1][j+1]
            else:
                right_diagonal += float('-inf')
            dp[i][j] = max(up, left_diagonal, right_diagonal)
	
    maxi = float('-inf')
    for j in range(m):
        maxi = max(dp[n-1][j], maxi)
    return maxi


def so_solve(n, m, arr):
    prev = [0] * m
    for j in range(m):
        prev[j] = arr[0][j]

    for i in range(1,n):
        temp = [0] *m
        for j in range(m):
            up = arr[i][j] + prev[j]
            left_diagonal = arr[i][j]
            if j-1>=0:
                left_diagonal += prev[j-1]
            else:
                left_diagonal += float('-inf')
            right_diagonal = arr[i][j]
            if j+1<m:
                right_diagonal += prev[j+1]
            else:
                right_diagonal += float('-inf')
            temp[j] = max(up, left_diagonal, right_diagonal)
        prev = temp
    return max(prev)



if __name__ == "__main__":
    matrix = [[1, 2, 10, 4], [100, 3, 2, 1], [1, 1, 20, 2], [1, 2, 2, 1]]

    n = len(matrix)
    m = len(matrix[0])
    dp = [[-1 for j in range(m)] for i in range(n)]
    maxi = float('-inf')
    for j in range(m):
        ans = solve(n-1,j, m, matrix, dp)
        maxi = max(maxi, ans)
    print(maxi)
    print(tab_solve(n, m, matrix))
    print(so_solve(n, m, matrix))
    
    # print(tab_solve(m,n, arr))
    # print(so_solve(m,n, arr))