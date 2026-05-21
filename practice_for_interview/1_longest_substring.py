def get_longest_substring_using_set(data):
    left=0
    char_set = set()

    max_len = 0
    start = 0
    
    for right in range(len(data)):
        # shrink until it gets valid
        while data[right] in char_set:
            char_set.remove(data[left])
            left+=1
        
        char_set.add(data[right])

        # update the answer
        if right-left+1> max_len:
            max_len = right-left+1
            start = left
    return data[start:start+max_len]

def get_longest_substring_using_hashmap(data):
    char_index = dict()
    left = 0

    start = 0
    max_len = 0

    for right in range(len(data)):
        # shrink until it gets valid
        if data[right] in char_index and char_index[data[right]]>=left:  ## dont forget to check if it is in window example abba
            left = char_index[data[right]]+1
        char_index[data[right]]=right

        # update the answer
        if right-left+1 > max_len:
            max_len = right-left+1
            start = left
    return data[start:start+max_len]

data = 'abascbb'
print(get_longest_substring_using_set(data))
print(get_longest_substring_using_hashmap(data))

# Test cases for edge cases
assert get_longest_substring_using_set("abba") == "ab"
assert get_longest_substring_using_set("abcabcbb") == "abc"
assert get_longest_substring_using_set("") == ""
assert get_longest_substring_using_set("a") == "a"