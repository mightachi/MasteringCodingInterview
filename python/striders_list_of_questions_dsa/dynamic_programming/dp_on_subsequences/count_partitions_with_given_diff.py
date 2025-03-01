def solve(ind:int, target:int, arr: list, dp:list[list]) -> int:
    if ind == 0:
        if target == 0 and arr[0] == 0:
            return 2
        if target == 0 or arr[ind] == target:
            return 1
        return 0

    if dp[ind][target] != -1:
        return dp[ind][target]
        
    not_taken = solve(ind-1, target, arr, dp)
    taken = 0
    if arr[ind]<=target:
        taken = solve(ind-1, target-arr[ind], arr,dp)

    dp[ind][target] = taken + not_taken
    return taken + not_taken

if __name__ == "__main__":
    arr = [5, 2, 6, 4]
    d = 3
    total_sum = sum(arr)
    n = len(arr)
    if (total_sum-d) % 2 != 0:
        print("0")
    if total_sum-d<0:
        print("0")
    target = (total_sum-d)//2
    dp = [[-1 for _ in range(target+1)] for _ in range(n)]
    print(solve(n-1, target, arr, dp))