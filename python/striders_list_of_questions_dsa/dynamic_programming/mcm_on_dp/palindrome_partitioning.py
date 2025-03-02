def solve(i,n,s,dp):
	if i>=n:
		return 0
	if dp[i] != -1:
		return dp[i]
	mini = int(1e9)
	for k in range(i,n):
		if isPalindrome(s,i,k):
			cost = 1 + solve(k+1,n,s,dp)
			mini = min(cost,mini)
	dp[i] = mini
	return mini

def isPalindrome(s,i,j):
        while i<j:
            if s[i] != s[j]:
                return False
            i+=1
            j-=1
        return True

str = "BABABCBADCEDE"
n=len(str)
dp = [-1 for _ in range(n)]
print(solve(0,n,str,dp)-1)