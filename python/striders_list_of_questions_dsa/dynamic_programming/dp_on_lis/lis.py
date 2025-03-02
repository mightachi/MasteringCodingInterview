def solve(ind,prev_ind,arr,dp):
    n = len(arr)
    if ind==n:
        return 0
    if dp[ind][prev_ind+1] != -1:
        return dp[ind][prev_ind+1]
    not_taken = solve(ind+1, prev_ind, arr, dp)
    taken = 0
    if prev_ind==-1 or arr[ind] > arr[prev_ind]:
        taken = 1 + solve(ind+1, ind, arr, dp)
    dp[ind][prev_ind+1] = max(taken,not_taken)
    return dp[ind][prev_ind+1]

if __name__ == "__main__":
    arr = [10, 9, 2, 5, 3, 7, 101, 18]
    n = len(arr)
    dp = [[-1 for _ in range(n+1)] for _ in range(n)]
    print(solve(0,-1,arr,dp))