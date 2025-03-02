def solve(arr):
	max_profit = 0
	mini = arr[0]
	n = len(arr)
	for i in range(1,n):
		cur_profit = arr[i] - mini
		max_profit = max(cur_profit, max_profit)
		mini = min(mini, arr[i])
	return max_profit


print(solve([7,1,5,3,6,4]))