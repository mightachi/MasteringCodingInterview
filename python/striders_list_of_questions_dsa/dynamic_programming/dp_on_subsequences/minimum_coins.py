def solve(ind:int, target: int, arr: list, dp:list[list]) -> int:
    if ind ==0:
        if target % arr[0] == 0:
            return target//arr[0]
        else:
            return int(1e9)

    if dp[ind][target] != -1:   
        return dp[ind][target]

    not_taken = 0 + solve(ind-1, target, arr, dp)
    taken = int(1e9)
    if arr[ind]<=target:
        taken = 1 + solve(ind, target - arr[ind], arr, dp)
    dp[ind][target] = min(taken, not_taken)
    return min(taken, not_taken)


if __name__ == "__main__":
    arr = [1, 2, 3]
    T = 7
    n = len(arr)
    dp = [[-1 for _ in range(T+1)] for _ in range(n)]
    print(solve(n-1, T, arr, dp))