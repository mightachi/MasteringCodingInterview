'''
Problem: https://codeforces.com/edu/course/2/lesson/4/1/practice/contest/273169/problem/A
A. Segment Tree for the Sum
Input:
5 5
5 4 2 3 5
2 0 3
1 1 1
2 0 3
1 3 1
2 0 5


Output:
11
8
14
'''
class segtree:
    def __init__(self, n:int):
        self.size = 1
        while self.size<n:
            self.size*=2
        self.sums = [0]*(2*self.size)

    def build_segment(self, arr, x, lx, rx):
        if rx-lx==1:
            if lx<len(arr):
                self.sums[x] = arr[lx]
            return
        m = (lx+rx)//2

        self.build_segment(arr, 2*x+1, lx, m)
        self.build_segment(arr, 2*x+2, m, rx)
        self.sums[x] = self.sums[2*x+1] + self.sums[2*x+2]

    def build(self, arr):
        self.build_segment(arr,0,0,self.size)
        pass
    
    def set_segment(self, i, v, x, lx, rx):
        if rx-lx == 1:
            self.sums[x] = v
            return
        m = (lx + rx)//2
        if i<m:
            self.set_segment(i,v,2*x+1,lx,m)
        else:
            self.set_segment(i,v,2*x+2,m,rx)
        self.sums[x] =  self.sums[2*x+1] + self.sums[2*x+2]

    def set(self,i,v):
        self.set_segment(i,v,0,0,self.size)
    
    def sum_segment(self, l, r, x, lx, rx):
        # No intersetion of the current segment with requested segment
        if lx>=r or l>=rx:
            return 0
        
        # Inside the requested segment
        if lx>=l and rx<=r:
            return self.sums[x]
        
        m = (lx+rx)//2

        # if it is in left subtree
        s1 = self.sum_segment(l,r,2*x+1,lx,m)

        # if it is in right subtree
        s2 = self.sum_segment(l,r,2*x+2,m,rx)
        return s1+s2

    def sum(self,l,r):
        return self.sum_segment(l,r, 0, 0, self.size)


n,m = map(int,input().strip().split())
arr = list(map(int,input().strip().split()))
st = segtree(n)
st.build(arr)
# for i,v in enumerate(arr):  # was having nlogn complexity since we were calling for each element set method which has logn
#     st.set(i,v)

while m>0:
    op,x,y = map(int, input().strip().split())
    if op == 1:
        st.set(x,y)
    elif op == 2:
        print(st.sum(x,y))
    m-=1
    