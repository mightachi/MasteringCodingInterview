def nStarTriangle(n: int) -> None:
    # Write your code here.
    for i in range(1,n+1):
        for j in range(i-1):
            print(" ",end="")
        for k in range(2*(n+1-i)-1):
            print("*",end="")
        print()
    pass