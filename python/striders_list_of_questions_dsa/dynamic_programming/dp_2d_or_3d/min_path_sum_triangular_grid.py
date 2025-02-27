def solve(i:int, j:int,n:int,  arr:list[list], dp:list[list])->int:
	if dp[i][j] !=-1:
		return dp[i][j]
	if i==n-1:
		return arr[i][j]
	
	bottom = arr[i][j] + solve(i+1,j,n,arr,dp)
	
	bottom_right = arr[i][j] + solve(i+1,j+1,n,arr,dp)

	dp[i][j] = min(bottom, bottom_right)
	return dp[i][j]

def tab_solve(n:int, arr:list[list])->int:
	dp = [[0 for j in range(n)] for i in range(n)]
	for j in range(n):
		dp[n-1][j] = arr[n-1][j]
	for i in range(n-2,-1,-1):
		for j in range(i,-1,-1):
			down = arr[i][j] + dp[i+1][j]
			diagonal = arr[i][j] + dp[i+1][j+1]
			dp[i][j] = min(down, diagonal)
	return dp[0][0]

def so_solve(n:int, arr:list[list])->int:
	front = [0] *n
	for j in range(n):
		front[j] = arr[n-1][j]
	for i in range(n-2, -1, -1):
		temp = [0] * n
		for j in range(i, -1,-1):
			down = arr[i][j] + front[j]
			diagonal = arr[i][j] + front[j+1]
			temp[j] = min(down, diagonal)
		front = temp
	return front[0]
    


if __name__ == "__main__":
    triangle = [[1], [2, 3], [3, 6, 7], [8, 9, 6, 10]]

    n = len(triangle)
    dp = [[-1 for j in range(n)] for i in range(n)]
    print(solve(0,0,n, triangle, dp))
    print(tab_solve(n, triangle))
    print(so_solve(n, triangle))