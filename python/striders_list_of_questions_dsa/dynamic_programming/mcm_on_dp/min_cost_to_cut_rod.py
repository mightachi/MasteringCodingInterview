def min_cost_cutting_rod(i,j,c,dp)->int:
    if i>j:
        return 0
    if dp[i][j] != -1:
        return dp[i][j]
    mini = int(1e9)
    for k in range(i,j+1):
        cost = min_cost_cutting_rod(i,k-1,c,dp) + min_cost_cutting_rod(k+1,j,c,dp) + (c[j+1]-c[i-1])
        mini = min(mini, cost)
    dp[i][j] = min(dp[i][j],cost)

    return dp[i][j]

cuts = [3, 5, 1, 4]
c = len(cuts)
n = 7
dp = [[-1 for _ in range(c+1)] for _ in range(c+1)]
cuts = [0] + cuts + [n]
cuts.sort()
print(min_cost_cutting_rod(1,c,cuts,dp))