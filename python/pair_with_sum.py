# Find the pair of item whose sum is equals to the target value

def pair_with_sum(data, target_sum):
    complement_dict = {}
    for index in range(0, len(data)):
        temp = target_sum - data[index]
        if temp in complement_dict:
            return True
        else:
            complement_dict[data[index]] = index
    return False

if pair_with_sum([8,0],8):
    print("The pair exist")
else:
    print("The pair does not exist")