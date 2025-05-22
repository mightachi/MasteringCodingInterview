class Solution:
    def isPalindrome(self, s):
        l = 0
        r = len(s)-1
        while l <= r:
            if s[l] != s[r]:
                return False
            l += 1
            r -= 1
        return True
    
    def longestPalindrome(self, s: str, t: str) -> int:
        concat_str = s + t
        n = len(concat_str)
        max_len = 1  # At least one character will be a palindrome
        
        # Check all possible substrings
        for i in range(n):
            for j in range(i+1, n):
                if self.isPalindrome(concat_str[i:j+1]):
                    max_len = max(max_len, j-i+1)
        
        return max_len

# Test cases
s = "b"
t = "aaaa"
sol = Solution()
print(sol.longestPalindrome(s,t))  # Should print 5 (for "baaaa")