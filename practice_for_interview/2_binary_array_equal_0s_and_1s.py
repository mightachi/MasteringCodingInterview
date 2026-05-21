def get_binary_array_of_equal_0s_and_1s(data):
    # Replace 0's with 1's 
    temp_data = [-1 if value == 0 else 1 for value in data]
    prefix_sum_map = {0:-1}
    prefix_sum = 0
    max_len = 0
    start = -1
    for index in range(len(temp_data)):
        prefix_sum+=temp_data[index]
        if prefix_sum in prefix_sum_map:
            length = index - prefix_sum_map[prefix_sum]
            if length > max_len:
                max_len = length
                start = prefix_sum_map[prefix_sum] + 1
        else:
            prefix_sum_map[prefix_sum] = index
    if max_len == 0:
        return []
            
    return data[start:start+max_len]

data = [1,0,1,1,0,1,0]
print(get_binary_array_of_equal_0s_and_1s(data))

# edge cases

assert get_binary_array_of_equal_0s_and_1s([]) == []
assert get_binary_array_of_equal_0s_and_1s([0,1]) == [0,1]
assert get_binary_array_of_equal_0s_and_1s([1,0]) == [1,0]
assert get_binary_array_of_equal_0s_and_1s([1,1,1]) == []
assert get_binary_array_of_equal_0s_and_1s([0,0,0]) == []
assert get_binary_array_of_equal_0s_and_1s([0]) == [] 
assert get_binary_array_of_equal_0s_and_1s([1]) == [] 
assert get_binary_array_of_equal_0s_and_1s([0,1,0,1]) == [0,1,0,1]
assert get_binary_array_of_equal_0s_and_1s([1,1,1,0,0,0]) == [1,1,1,0,0,0] 
assert get_binary_array_of_equal_0s_and_1s([0,1,1,0]) == [0,1,1,0]
assert get_binary_array_of_equal_0s_and_1s([0,0,0,0,1,1,0]) == [0,0,1,1]
assert get_binary_array_of_equal_0s_and_1s([0,1,1,0,0,0,0]) == [0,1,1,0]