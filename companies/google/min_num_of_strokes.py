'''
Problem: https://codeforces.com/problemset/problem/448/C
Input:
5
2 2 1 2 1
 
Output
3
'''
import sys
sys.setrecursionlimit(10**6)
class segtree:
    def __init__(self, n:int):
        self.size = 1
        while self.size<n:
            self.size*=2
        self.values = [(0,-1)]*(2*self.size)
 
    def build_segment(self, arr, x, lx, rx):
        if rx-lx==1:
            if lx<len(arr):
                self.values[x] = (arr[lx],lx)
            return
        m = (lx+rx)//2
 
        self.build_segment(arr, 2*x+1, lx, m)
        self.build_segment(arr, 2*x+2, m, rx)
        if self.values[2*x+1][0] < self.values[2*x+2][0]:
            self.values[x] = self.values[2*x+1]
        else:
            self.values[x] = self.values[2*x+2]
 
    def build(self, arr):
        self.build_segment(arr,0,0,self.size)
        pass
    
    def calculate_min(self, l, r, x, lx, rx):
        # No intersetion of the current segment with requested segment
        if lx>=r or l>=rx:
            return (float('inf'), -1)
        
        # Inside the requested segment
        if lx>=l and rx<=r:
            return self.values[x]
        
        m = (lx+rx)//2
 
        # if it is in left subtree
        min1 = self.calculate_min(l,r,2*x+1,lx,m)
 
        # if it is in right subtree
        min2 = self.calculate_min(l,r,2*x+2,m,rx)
        if min1[0]<min2[0]:
            return min1
        else:
            return min2
 
    def calculate(self,l,r):
        return self.calculate_min(l,r, 0, 0, self.size)
 
n = int(input().strip())
board = list(map(int, input().strip().split()))
n = 5000
board = [10**9]*n
 
st = segtree(n)
st.build(board)
 
def calculate_min_stoke(l, r, h):
    if l>=r:
        return 0
    m = l
    mini,m = st.calculate(l,r)
    return min(r-l, board[m]-h+ calculate_min_stoke(l,m,board[m])+calculate_min_stoke(m+1,r,board[m]))
 
 
print(calculate_min_stoke(0,n,0))