def no_of_lis(arr):
	n = len(arr)
	dp = [1] *n
	ct = [1] *n
	maxi = -int(1e9)
	for i in range(n):
		for j in range(i):
			if arr[j]<arr[i] and 1 + dp[j] > dp[i]:
				dp[i] = 1 + dp[j]
				ct[i] = ct[j]
				maxi = max(maxi, dp[i])
			elif arr[j]<arr[i] and 1+dp[j] == dp[i]:
				ct[i] += ct[j]
	
	ans=0
	for i in range(n):
		if dp[i] == maxi:
			ans+=ct[i]
	return ans

arr = [1, 5, 4, 3, 2, 6, 7, 2]
print(no_of_lis(arr))