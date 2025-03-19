'''
Problem: https://codeforces.com/edu/course/2/lesson/4/1/practice/contest/273169/problem/B
B. Segment Tree for the Minimum

Input:
5 5
5 4 2 3 5
2 0 3
1 2 6
2 0 3
1 3 1
2 0 5

Output:
2
4
1

'''

class segtree:
    def __init__(self, n:int):
        self.size = 1
        while self.size<n:
            self.size*=2
        self.values = [0]*(2*self.size)

    def build_segment(self, arr, x, lx, rx):
        if rx-lx==1:
            if lx<len(arr):
                self.values[x] = arr[lx]
            return
        m = (lx+rx)//2

        self.build_segment(arr, 2*x+1, lx, m)
        self.build_segment(arr, 2*x+2, m, rx)
        self.values[x] = min(self.values[2*x+1], self.values[2*x+2])

    def build(self, arr):
        self.build_segment(arr,0,0,self.size)
        pass
    
    def set_segment(self, i, v, x, lx, rx):
        if rx-lx == 1:
            self.values[x] = v
            return
        m = (lx + rx)//2
        if i<m:
            self.set_segment(i,v,2*x+1,lx,m)
        else:
            self.set_segment(i,v,2*x+2,m,rx)
        self.values[x] =  min(self.values[2*x+1],self.values[2*x+2])

    def set(self,i,v):
        self.set_segment(i,v,0,0,self.size)
    
    def calculate_min(self, l, r, x, lx, rx):
        # No intersetion of the current segment with requested segment
        if lx>=r or l>=rx:
            return float('inf')
        
        # Inside the requested segment
        if lx>=l and rx<=r:
            return self.values[x]
        
        m = (lx+rx)//2

        # if it is in left subtree
        min1 = self.calculate_min(l,r,2*x+1,lx,m)

        # if it is in right subtree
        min2 = self.calculate_min(l,r,2*x+2,m,rx)
        return min(min1,min2)

    def calculate(self,l,r):
        return self.calculate_min(l,r, 0, 0, self.size)
    


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
        print(st.calculate(x,y))
    m-=1
    