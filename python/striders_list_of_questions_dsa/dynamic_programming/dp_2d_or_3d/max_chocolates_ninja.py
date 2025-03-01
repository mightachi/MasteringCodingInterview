def solve(i:int, j1:int, j2:int,n:int, m:int,  arr:list[list], dp:list[list[list]]):
    if j1<0 or j1>=m or j2<0 or j2>=m:
        return float('-inf')
    if i==n-1:
        if j1==j2:
            return arr[i][j1]
        else:
            return arr[i][j1] + arr[i][j2]

    if dp[i][j1][j2] != -1:
        return dp[i][j1][j2]

    maxi = float('-inf')
    for d1 in range(-1,2):
        for d2 in range(-1,2):
            ans = 0
            if j1==j2:
                ans = arr[i][j1] + solve(i+1,j1+d1,j2+d2, n,m,arr,dp)
            else:
                ans = arr[i][j1] + arr[i][j2] + solve(i+1,j1+d1,j2+d2,n,m,arr,dp)
            maxi = max(maxi, ans)
    dp[i][j1][j2] = maxi
    return maxi

def tab_solve(n:int, m:int, arr:list[list]):
	dp = [[[0 for _ in range(m)] for j in range(m)] for i in range(n)]
	
	for j1 in range(m):
		for j2 in range(m):
			if j1==j2:
				dp[n-1][j1][j2] = arr[n-1][j1]
			else:
				dp[n-1][j1][j2] = arr[n-1][j1] + arr[n-1][j2]
	
	for i in range(n-2, -1, -1):
		for j in range(m):
			for k in range(m):
				maxi = float('-inf')
				for d1 in range(-1, 2):
					for d2 in range(-1, 2):
						ans = 0
						if j==k:
							ans = arr[i][j]
						else:
							ans = arr[i][j] + arr[i][k]
						if j+d1<0 or j+d1>=m or k+d2<0 or k+d2 >=m:
							ans+= float('-inf')
						else:
							ans+= dp[i+1][j+d1][k+d2]
						maxi = max(maxi, ans)
				dp[i][j][k] = maxi
	
	return dp[0][0][m-1]


def so_solve(n:int, m:int, arr:list[list]) -> int:
    front = [[0 for _ in range(m)] for _ in range(m)]
    cur = [[ 0 for _ in range(m)] for _ in range(m)]

    for j1 in range(m):
        for j2 in range(m):
            if j1==j2:
                front[j1][j2] = arr[n-1][j1]
            else:
                front[j1][j2] = arr[n-1][j1] + arr[n-1][j2]

    for i in range(n-2, -1, -1):
        for j1 in range(m):
            for j2 in range(m):
                maxi = float('-inf')
                
                for d1 in range(-1, 2):
                    for d2 in range(-1, 2):
                        ans = 0
                        if j1==j2:
                            ans = arr[i][j1]
                        else:
                            ans = arr[i][j1] + arr[i][j2]
                        
                        if j1+d1<0 or j1+d1>=m or j2+d2<0 or j2+d2>=m:
                            ans+= float('-inf')
                        else:
                            ans+= front[j1+d1][j2+d2]
                        maxi = max(maxi, ans)
                cur[j1][j2] = maxi
        front = [row[:] for row in cur]
    return front[0][m-1]


if __name__ == "__main__":
    matrix = [[2, 3, 1, 2], [3, 4, 2, 2], [5, 6, 3, 5]]
    n = len(matrix)
    m = len(matrix[0])
    dp = [[[-1 for k in range(m)] for j in range(m)] for i in range(n)]
    print(solve(0,0,m-1,n,m,matrix, dp))
    print(tab_solve(n,m,matrix))
    print(so_solve(n,m,matrix))