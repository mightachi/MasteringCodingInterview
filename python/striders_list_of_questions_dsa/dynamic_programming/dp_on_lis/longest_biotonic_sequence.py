def longest_biotonice_sequence(arr):
	n = len(arr)
	dp1 = [1]*n
	dp2 = [1]*n
	
	for i in range(n):
		for j in range(i):
			if arr[j]<arr[i] and 1 + dp1[j] > dp1[i]:
				dp1[i] = 1+dp1[j]
	
	for i in range(n-1,-1,-1):
		for j in range(n-1,i,-1):
			if arr[j]<arr[i] and 1+dp2[j] > dp2[i]:
				dp2[i] = 1 + dp2[j]

	maxi = -int(1e9)
	for i in range(n):
		maxi = max(maxi, dp1[i]+dp2[i]-1)
	return maxi

arr = [1, 11, 2, 10, 4, 5, 2, 1]
print(longest_biotonice_sequence(arr))