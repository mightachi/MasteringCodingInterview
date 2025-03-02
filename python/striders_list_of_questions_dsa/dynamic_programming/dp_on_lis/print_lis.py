def print_lis(arr):
	n = len(arr)
	dp = [1] * n
	predecessor = [None] * n

	# calculated the length of LIS
	for i in range(n):
		for j in range(i):
			if arr[j]<arr[i] and dp[i]< 1+ dp[j]:
				dp[i] = 1+ dp[j]
				predecessor[i] = j

	# calculate the max_lenth of LIS
	max_len = 0
	max_len_ind = -1
	for i in range(n):
		if dp[i] > max_len:
			mac_len = dp[i]
			max_len_in = i

	# Reconstruct the LIS
	l = []
	current_index = max_len_ind
	while current_index is not None:
		l.append(arr[current_index])
		current_index = predecessor[current_index]
	return l[::-1]

if __name__ == "__main__":
    arr = [10,9,2,5,3,7,101,18]
    print(print_lis(arr))