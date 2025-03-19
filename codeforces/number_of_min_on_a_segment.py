'''
Problem: https://codeforces.com/edu/course/2/lesson/4/1/practice/contest/273169/problem/C
C. Number of Minimums on a Segment

Input:
5 5
3 4 3 5 2
2 0 3
1 1 2
2 0 3
1 0 2
2 0 5

Output:
3 2
2 1
2 3
'''

class segtree:
    NEUTRAL_ELEMENT = (float('inf'), 0 )
    def __init__(self, n:int):
        self.size = 1
        while self.size<n:
            self.size*=2
        self.values = [(0,0)]*(2*self.size)

    def merge(self, min_x, min_y):
        if min_x[0]<min_y[0]:
            return min_x
        elif min_y[0]<min_x[0]:
            return min_y
        else:
            return (min_x[0],min_x[1]+min_y[1])
    
    def single(self, v):
        return (v, 1)
    
    def build_segment(self, arr, x, lx, rx):
        if rx-lx==1:
            if lx<len(arr):
                self.values[x] = self.single(arr[lx])
            return
        m = (lx+rx)//2

        self.build_segment(arr, 2*x+1, lx, m)
        self.build_segment(arr, 2*x+2, m, rx)
        self.values[x] = self.merge(self.values[2*x+1], self.values[2*x+2])

    def build(self, arr):
        self.build_segment(arr,0,0,self.size)
        pass
    
    def set_segment(self, i, v, x, lx, rx):
        if rx-lx == 1:
            self.values[x] = self.single(v)
            return 
        m = (lx + rx)//2
        if i<m:
            self.set_segment(i,v,2*x+1,lx,m)
        else:
            self.set_segment(i,v,2*x+2,m,rx)
        self.values[x] =  self.merge(self.values[2*x+1],self.values[2*x+2])

    def set(self,i,v):
        self.set_segment(i,v,0,0,self.size)
    
    def calculate_min(self, l, r, x, lx, rx):
        # No intersetion of the current segment with requested segment
        if lx>=r or l>=rx:
            return segtree.NEUTRAL_ELEMENT
        
        # Inside the requested segment
        if lx>=l and rx<=r:
            return self.values[x]
        
        m = (lx+rx)//2

        # if it is in left subtree
        min1 = self.calculate_min(l,r,2*x+1,lx,m)

        # if it is in right subtree
        min2 = self.calculate_min(l,r,2*x+2,m,rx)
        return self.merge(min1,min2)

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
        result = st.calculate(x,y)
        print(str(result[0]) + " " + str(result[1]))
    m-=1
    