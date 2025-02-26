def count_climbing_ways(stairs:int) -> int:
	dp = [-1] * (stairs+1)
	
	# Base Cases
	dp[0] = 1
	dp[1] = 1
	for i in range(2, stairs+1):
		dp[i] = dp[i-1] + dp[i-2]
	return dp[stairs]

def climbStairs(steps:int) -> int:
	prev2 = 1
	prev = 1
	if steps==1:
		return prev
	elif steps==2:
		return 2
	else:
		for step in range(2, steps+1):
			current = prev+prev2
			prev2 = prev
			prev = current
		return current

print(climbStairs(4))

print(count_climbing_ways(4))