def solve(n:int, height:list, k:int, dp: list):
	# base case
	if n==0:
		dp[0] = 0
		return 0
	if dp[n] != -1:
		return dp[n]
	
	mmSteps = float('inf')

	for i in range(1, k+1):
		if n-i>=0:
			jump = solve(n-i, height, k, dp) + abs(height[n] - height[n-i])
			mmSteps = min(jump, mmSteps)
	dp[n] = mmSteps
	return dp[n]


def tab_solve(n:int, height:list, k:int):
    #base case
    if n==0:
        return 0
    dp[0] = 0

    for j in range(1, n):
        mmSteps = float('inf')
        for i in range(1, k+1):
            if j-i >=0:
                jump = dp[j-i] + abs(height[j] - height[j-i])
                mmSteps = min(mmSteps, jump)
        dp[j] = mmSteps
    return dp[n-1]



if __name__ == "__main__":
    height = [30, 10, 60, 10, 60, 50]
    n = len(height)
    dp = [-1] * n
    k = 2
    print(solve(n-1, height, k, dp))
    print(tab_solve(n, height, k))
   