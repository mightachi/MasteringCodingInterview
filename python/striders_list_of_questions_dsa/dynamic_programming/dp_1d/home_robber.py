def solve(n, arr, dp):
    if n==0:
        dp[0]=arr[0]
        return arr[0]
    if dp[n] != -1:
        return dp[n]
    if n<0:
        return 0
    
    pick = arr[n] + solve(n-2, arr, dp)
    non_pick = solve(n-1, arr, dp)

    dp[n] = max(pick, non_pick)
    return dp[n]


    
if __name__ == "__main__":
    arr = [1, 5, 1, 2, 6]
    n = len(arr)
    dp = [-1] * (n-1)
    ans1 = solve(n-2, arr[:-1], dp)
    dp = [-1] * (n-1)
    ans2 = solve(n-2, arr[1:], dp)
    print(max(ans1, ans2))