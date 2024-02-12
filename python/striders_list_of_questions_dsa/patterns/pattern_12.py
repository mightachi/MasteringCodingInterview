def numberCrown(n: int) -> None:
    # Write your solution here.
    for i in range(1,n+1):
       # numbers
        for j in range(1,i+1):
            print(j,end=" ")
       # spaces
        for _ in range(2*(n-i)):
            print(" ",end="")
       # numbers
        for k in range(i,0,-1):
            print(k,end=" ")
        print()
    pass