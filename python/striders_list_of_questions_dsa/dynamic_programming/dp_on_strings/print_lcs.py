def lcs(s1,s2):
	n = len(s1)
	m = len(s2)
	dp = [[-1 for _ in range(m+1)] for _ in range(n+1)]
	for i in range(n+1):
		dp[i][0] = 0
	for j in range(m+1):
		dp[0][j] = 0
	for i in range(1,n+1):
		for j in range(1, m+1):
			if s1[i-1] == s2[j-1]:
				dp[i][j] = 1 + dp[i-1][j-1]
			else:
				dp[i][j] = max(dp[i-1][j], dp[i][j-1])
	
	len_ = dp[n][m]
	str_ = ""
	
	ind1 = n
	ind2 = m
	while ind1>0 and ind2>0:
		if s1[ind1-1]== s2[ind2-1]:
			str_ = s1[ind1-1] + str_
			ind1-=1
			ind2-=1
		elif dp[ind1-1][ind2]>dp[ind1][ind2-1]:
			ind1-=1
		else:
			ind2-=1
	return str_

if __name__ == "__main__":
    s1 = "abcde"
    s2 = "bdgek"
    
    print(lcs(s1, s2))

