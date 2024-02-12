'''
/*
Problem Link: https://www.codingninjas.com/studio/problems/n-2-forest_6570178?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems&leftPanelTabValue=PROBLEM
*/
'''
def nForest(n:int) ->None:
    # Write your solution here.
    for i in range(1,n+1):
        for j in range(i):
            print("*",end=" ")
        print()
    pass