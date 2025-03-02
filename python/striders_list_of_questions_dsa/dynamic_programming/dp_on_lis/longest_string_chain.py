def is_predecessor(s1,s2):
	if len(s1) != len(s2) +1:
		return False
	first = 0
	second = 0
	while first < len(s1):
		if second < len(s2) and s1[first] == s2[second]:
			first+=1
			second +=1
		else:
			first+=1
	return first == len(s1) and second == len(s2)

def logest_string_chaing(words)->int:
	words.sort(key=len)
	n = len(words)
	dp = [1]*n
	maxi = -int(1e9)
	for i in range(n):
		for j in range(i):
			if is_predecessor(words[i],words[j]) and dp[j] + 1 > dp[i]:
				dp[i] = dp[j]+1
				maxi = max(maxi, dp[i])
	return maxi

words = ["a", "b", "ba", "bca", "bda", "bdca"]
print(logest_string_chaing(words))