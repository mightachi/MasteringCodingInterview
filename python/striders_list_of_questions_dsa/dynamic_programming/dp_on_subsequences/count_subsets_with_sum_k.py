def solve(ind:int, target, arr:list, dp:list[list]) -> int:
    if ind == 0:
        if arr[ind]==0 and target==0:
            return 2
        if arr[0] == target or target==0:
            return 1
        return 0
    if dp[ind][target] != -1:
        return dp[ind][target]
    not_taken = solve(ind-1, target, arr, dp)
    taken = 0
    if arr[ind]<= target:
        taken = solve(ind-1, target - arr[ind], arr, dp)
    dp[ind][target] = taken + not_taken
    return taken + not_taken



if __name__ == "__main__":
    arr = [1, 2, 2, 3] # output: 3
    k = 3
    arr = [28,4,3,27,0,24,26] # output: 2
    k = 24
    n = len(arr)
    dp = [[-1 for _ in range(k+1)] for _ in range(n)]
    print(solve(n-1, k, arr, dp))
