def can_jump(data):
    farthest = 0
    for i in range(len(data)):
        if farthest < i:
            return False
        
        farthest = max(farthest, i+data[i])
    return True

assert can_jump([0]) == True
assert can_jump([0,1]) == False
assert can_jump([2,0,0]) == True
assert can_jump([3,2,1,0,4]) == False