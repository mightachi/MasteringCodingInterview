def solve(m, n, arr, dp):
	if m==0 and n==0:
		dp[0][0] = arr[m][n]
		return dp[0][0]
	if m<0 or n<0:
		return float('inf')
	
			
	up = arr[m][n] +  solve(m-1,n,arr,dp)
	left = arr[m][n] + solve(m,n-1, arr, dp)
	dp[m][n] = min(up, left)
	return dp[m][n]

def tab_solve(m, n, arr):
    dp = [[-1 for j in range(n)] for i in range(m)]
    for i in range(m):
        for j in range(n):
            if i==0 and j==0:
                dp[0][0] = arr[0][0]
            else:
                up = arr[i][j]
                if i>0:
                    up+= dp[i-1][j]
                else:
                    up+= float('inf')
                left = arr[i][j]
                if j>0:
                    left += dp[i][j-1]
                else:
                    left += float('inf')
                dp[i][j] = min(up, left)
    return dp[m-1][n-1]

def so_solve(m, n, arr):
    prev = [0] * n
    for i in range(m):
        temp = [0] * n
        for j in range(n):
            if i==0 and j==0:
                temp[j] = arr[i][j]
            else:
                up = arr[i][j]
                if i > 0:
                    up += prev[j]
                else:
                    up += float('inf')
                left = arr[i][j]
                if j > 0:
                    left += temp[j-1]
                else:
                    left += float('inf')
                temp[j] = min(up, left)
        prev = temp
    return prev[n-1]

if __name__ == "__main__":
    arr = [[5, 9, 6],
              [11, 5, 2]]

    m = len(arr)
    n = len(arr[0])
    dp = [[-1 for j in range(n)] for i in range(m)]
    print(solve(m-1,n-1, arr, dp))
    print(tab_solve(m,n, arr))
    print(so_solve(m,n, arr))