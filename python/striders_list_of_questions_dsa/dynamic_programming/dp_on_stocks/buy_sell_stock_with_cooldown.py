def solve(ind,buy,arr,dp):
    n = len(arr)
    if ind>=n:
        return 0
    if dp[ind][buy] != -1:
        return dp[ind][buy]
    if buy == 0:
        op1 = solve(ind+1, buy, arr, dp)
        op2 = -arr[ind] + solve(ind+1, 1,arr,dp)
    elif buy == 1:
        op1 = solve(ind+1, buy, arr, dp)
        op2 = arr[ind] + solve(ind+2, 0, arr,dp)
    dp[ind][buy] = max(op1, op2)
    return max(op1, op2)

if __name__ == "__main__":
    prices = [4, 9, 0, 4, 10]
    dp = [[-1 for _ in range(2)] for _ in range(len(prices))]
    print(solve(0,0,prices, dp))
