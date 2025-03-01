def solve(ind:int, target:int, arr:list[list], dp:list[list]) -> bool:
    if target == 0:
        return True

    if ind==0:
        return arr[ind] == target

    if dp[ind][target] != -1:
        return dp[ind][target]
    not_taken = solve(ind-1, target, arr, dp)
    taken = False
    if (arr[ind]<=target):
        taken = solve(ind-1, target-arr[ind], arr, dp)
    dp[ind][target] = not_taken or taken
    return taken or not_taken

if __name__ == "__main__":
    # Test case 1 output: true
    arr = [1, 2, 3, 4]
    k = 4
    # Test case 2 output: true
    arr = [3,34,4,12,5,2] 
    k =9
    
    n = len(arr)
    dp = [[-1 for _ in range(k+1)] for _ in range(n)]
    print(solve(n-1, k, arr, dp))
