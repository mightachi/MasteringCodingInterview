def lis_using_bs(arr)-> int:
	tails = []
	
	for num in arr:
		if not tails or num > tails[-1]:
			tails.append(num)
		else:
			left, right = 0, len(tails)-1
			while left<=right:
				mid = (left + right)//2
				if tails[mid] < num:
					left = mid +1
				else:
					right = mid-1
			tails[left] = num
	return len(tails)
arr = [10, 9, 2, 5, 3, 7, 101, 18]
print(lis_using_bs(arr))