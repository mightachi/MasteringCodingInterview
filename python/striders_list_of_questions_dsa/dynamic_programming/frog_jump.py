'''
def frogJump(n: int, height:list) -> int:
	if n==1:
		return 0
	if n==2:
		return height[1]-height[0]
	prev2 = 0
	prev = height[1]-height[0]
	for i in range(2, n):
		current = min(abs(height[i]-height[i-1]),abs(height[i]-height[i-2]))
		prev2 = prev
		prev = current
	
	return current

n=4
heights = [10,20,30,10]
print(frogJump(n, heights))
'''

def solve(n:int, height:list, dp:list) -> int:
    if n==0:
        dp[0]=0
        return 0
    if dp[n] != -1:
        return dp[n]
    jumpOne = solve(n-1, height, dp) + abs(height[n]-height[n-1])
    jumpTwo = float('inf')
    if n>1:
        jumpTwo = solve(n-2, height, dp) + abs(height[n]-height[n-2])

    dp[n] = min(jumpOne, jumpTwo)
    
    return dp[n]

def tab_solve(n:int, height:list)-> int:
    dp = [-1 for _ in range(n)]
    dp[0]=0
    if n==0:
        return 0
    for ind in range(1, n):
        jumpTwo = float('inf')
        jumpOne = dp[ind-1] + abs(height[ind]-height[ind-1])
        if ind > 1:
            jumpTwo = dp[ind-2] + abs(height[ind]-height[ind-2])
        dp[ind] = min(jumpOne, jumpTwo)
    
    return dp[n-1]


def so_solve(n:int, height:list) -> int:
	prev2=None
	prev=0
	if n==0:
		return 0
	for ind in range(1, n):
		jumpOne = prev + abs(height[ind] - height[ind-1])
		jumpTwo = float('inf')
		if ind>1:
			jumpTwo = prev2 + abs(height[ind] - height[ind-2])
		curr = min(jumpOne, jumpTwo)
		prev2 = prev
		prev = curr
	return curr


if __name__ == "__main__":
    height = [30, 10, 60, 10, 60, 50]
    n = len(height)
    dp = [-1] * n
    print(solve(n-1, height, dp))
    print(tab_solve(n, height))
    print(so_solve(n, height))
