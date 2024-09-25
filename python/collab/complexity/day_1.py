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

def permute(string, l, r):
    if l == r:
        print(string)
    else:
        for i in range(l, r + 1):
            string = swap(string, l, i)
            permute(string, l + 1, r)
            string = swap(string, l, i)  # backtrack

def swap(string, i, j):
    char_list = list(string)
    char_list[i], char_list[j] = char_list[j], char_list[i]
    return ''.join(char_list)

# Example usage
s = "ABC"
n = len(s)
permute(s, 0, n - 1)
