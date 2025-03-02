def partition_arr_for_max_sum(arr,k):
    n = len(arr)
    def f(ind,dp):
        if ind==n:
            return 0
        if dp[ind] != -1:
            return dp[ind]
        
        max_val = -int(1e9)
        ans = -int(1e9)
        len_val = 0
        for i in range(ind,min(ind+k,n)):
            len_val+=1
            max_val = max(arr[i],max_val)
            summation = len_val * max_val + f(i+1,dp)
            ans = max(ans,summation)
        dp[ind]=ans
        return ans
    dp = [-1]*n
    return f(0,dp)

num = [1, 15, 7, 9, 2, 5, 10]
k = 3
print(partition_arr_for_max_sum(num,k))