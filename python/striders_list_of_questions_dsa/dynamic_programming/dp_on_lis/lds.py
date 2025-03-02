def lds(arr):
	arr.sort()
	n = len(arr)
	dp = [1] * n
	predecessor = [None] * n
	
	# Create the LIS
	for i in range(n):
		for j in range(i):
			if arr[i]%arr[j]==0 and 1+dp[j] > dp[i]:
				dp[i] = 1+dp[j]
				predecessor[i] =j 
	
	# Get the max_len and its index
	max_len = 0
	max_len_idx = -1
	for i in range(n):
		if max_len < dp[i]:
			max_len = dp[i]
			max_len_idx = i
	
	ans = []
	# Reconstruct the LDS
	current_idx = max_len_idx
	while current_idx is not None:
		ans.append(arr[current_idx])
		current_idx = predecessor[current_idx]
	return ans[::-1]

arr = [1, 16, 7, 8, 4]
print(lds(arr))