'''
Problem: https://codeforces.com/problemset/problem/4/A

Input:
8

Output:
YES
'''

w = int(input().strip())
x = 2
while x <= w//2 and x%2 == 0 and (w-x)%2 != 0:
    x += 2
if x > w//2:
    print("NO")
else:
    print("YES")
