def sum(array):
    '''
    n: length of input
    time complexity f(n): 1+n*1+1 
    select dominant term: n
    time complexity O(n)
    
    '''
    total = 0  # constant operation 1
    # total runtime would be: n*1
    for i in range(len(array)): # the operation inside it will run n times
        total+=array[i] # constant operation 1
    return total # constant operation 1

def linear_search(array, target):
    for item in array:
        if item==target:
            return item
    return -1

def linear_search(array, target):
    for index in range(len(array)):
        if array[index]==target:
            return index
    return -1

'''Understading how to calculate time complexity of recursive function
Certainly! I'll explain the complexity and recursion for the given permutation algorithm with the input "ABC". Let's break it down step by step.
Recursion Explanation:
The permute function is recursive. It works as follows:
1. Base case: When l == r, it prints the current permutation.
2. Recursive case: It swaps the character at index l with each character from l to r, then recursively calls itself with l + 1.
3. After each recursive call, it swaps back (backtracking) to undo the change.
For "ABC", the recursion tree looks like this:
                 ABC
           /      |      \
         ABC     BAC     CBA
        /  \     /  \     /  \
      ABC ACB   BAC BCA CBA CAB

2. Complexity Analysis:
Time Complexity: O(n!)
Space Complexity: O(n)
Explanation:
- There are n! permutations for a string of length n.
- The depth of the recursion tree is n.
- At each level, we perform O(n) work (the for loop and swap operations).
Therefore, the time complexity is O(n n!) which simplifies to O(n!).
The space complexity is O(n) due to the recursion stack depth.
3. Detailed Recursion Steps for "ABC":

permute("ABC", 0, 2)
  i=0: ABC -> permute("ABC", 1, 2)
    i=1: ABC -> permute("ABC", 2, 2)
      print ABC
    i=2: ACB -> permute("ACB", 2, 2)
      print ACB
  i=1: BAC -> permute("BAC", 1, 2)
    i=1: BAC -> permute("BAC", 2, 2)
      print BAC
    i=2: BCA -> permute("BCA", 2, 2)
      print BCA
  i=2: CBA -> permute("CBA", 1, 2)
    i=1: CBA -> permute("CBA", 2, 2)
      print CBA
    i=2: CAB -> permute("CAB", 2, 2)
      print CAB

Each level of indentation represents a recursive call. The algorithm explores all possible permutations by swapping characters and making recursive calls.
4. Number of Operations:
- Number of recursive calls: 1 + 3 + 6 = 10
- Number of swaps: 2 (3 + 6) = 18
- Number of prints: 6
The total number of operations grows factorially with the input size, which is why the time complexity is O(n!).
This algorithm efficiently generates all permutations of the input string using backtracking, but it becomes impractical for large inputs due to its factorial time complexity.
'''
def permute(string, l, r):
    if l == r:
        print(string)
    else:
        for i in range(l, r + 1):
            print(f"Inside permute: i: {i}, l: {l}, r: {r}")
            string = swap(string, l, i)
            print(f"Inside permute: string: {string}")
            print(f"Calling permute with new l: {l+1}, r: {r}")
            permute(string, l + 1, r)
            print(f"Backtracking where i: {i}, l: {l}, r: {r}")
            string = swap(string, l, i)  # backtrack
            print(f"Inside permute: string: {string}")
def swap(string, i, j):
    print(f"Inside swap: i: {i}, j: {j}")
    char_list = list(string)
    print(f"Inside swap before swap: char_list: {char_list}")
    char_list[i], char_list[j] = char_list[j], char_list[i]
    print(f"Inside swap after swap: char_list: {char_list}")
    return ''.join(char_list)

# Example usage
s = "ABC"
n = len(s)
permute(s, 0, n - 1)
