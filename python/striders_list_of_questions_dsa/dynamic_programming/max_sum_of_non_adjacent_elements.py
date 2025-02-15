def solve(ind:int, arr:list, dp: list) -> int:
	if ind==0:
		dp[0] = arr[0]
		return arr[0]
	if ind<0:
		return 0
	if dp[ind] != -1:
		return dp[ind]

	pick = arr[ind] + solve(ind-2, arr, dp)
	non_pick = solve(ind-1, arr, dp)
	dp[ind] = max(pick, non_pick)
	return dp[ind]


def tab_solve(ind:int, arr:list) -> int:
    dp = [-1 for _ in range(n)]
    dp[0] = arr[0]
    if ind==0:
        return arr[0]
    if ind<0:
        return 0
    for i in range(1, ind):
        pick = arr[i]
        if i>1:
            pick+= dp[i-2]
        non_pick = dp[i-1]
        dp[i] = max(pick, non_pick)
    return dp[ind-1]


def so_solve(ind:int, arr:list) -> int:
	prev2 = 0
	prev = arr[0]
	if ind==0:
		return prev
	if ind<0:
		return 0
	for i in range(1, ind):
		pick = arr[i]
		if i > 1:
			pick = arr[i] + prev2
		non_pick = prev
		curr = max(pick, non_pick)
		prev2 = prev
		prev = curr
	return curr


def house_robber(arr:list):
	arr1 = arr[:-1]
	arr2 = arr[1:]
	n1 = len(arr1)
	n2 = len(arr2)
	ans1 = so_solve(n1, arr1)
	ans2 = so_solve (n2, arr2)
	return max(ans2, ans1)


if __name__ == '__main__':
    arr = [2, 1, 4, 9]
    n = len(arr)
    dp = [-1 for _ in range(n)]
    # Call the solve function and print the result
    print(solve(n-1, arr, dp))
    print(tab_solve(n, arr))
    print(so_solve(n, arr))

    arr = [1, 5, 1, 2, 6]
    house_robber(arr)