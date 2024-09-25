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
