from typing import List
class Solution:
    def minCosts(self, cost: List[int]) -> List[int]:
        n = len(cost)
        for i in range(n-1,0,-1):
            mini = cost[i]
            for j in range(i-1,-1,-1):
                mini = min(mini, cost[j])
            cost[i] = mini
        return cost


cost = [1,2,4,6,7]
cost = [5,3,4,1,3,2] # [5,4,3,3,2,1] # [5,3,3,1,1,1]
sol = Solution()
print(sol.minCosts(cost))