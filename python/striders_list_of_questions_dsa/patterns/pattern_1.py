'''
/*
Problem Link: https://www.codingninjas.com/studio/problems/n-forest_6570177?utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_patternproblems
*/
'''
def print_pattern(N):
    for i in range(N):
        for j in range(N):
            print("*", end="")
        print()
    
print_pattern(3)