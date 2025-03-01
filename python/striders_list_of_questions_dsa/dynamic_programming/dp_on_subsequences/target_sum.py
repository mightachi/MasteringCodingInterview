def solve(ind:int, target: int, arr: list, dp: list[list]) -> int:
    if ind == 0:
        if arr[ind] == 0 and target ==0:
            return 2
        if target == 0 or target == arr[ind]:
            return 1
        return 0
    if dp[ind][target] != -1:
        return dp[ind][target]

    not_taken = solve(ind-1, target, arr, dp)
    taken = 0
    if arr[ind]<= target:
        taken = solve(ind-1, target-arr[ind], arr, dp)
    dp[ind][target] = taken + not_taken
    return taken + not_taken


if __name__ == "__main__":
    arr = [1, 2, 3, 1]
    target = 3
    n = len(arr)
    total_sum = sum(arr)
    if total_sum-target<0:
        print(0)
    if (total_sum-target) % 2 != 0:
        print(0)
    T = (total_sum-target)//2
    dp = [[-1 for _ in range(T+1)] for _ in range(n)]
    print(solve(n-1,T,arr,dp))


