def largest_area_histogram(arr):
    stack = []
    max_area = 0
    n = len(arr)
    for i, height in enumerate(arr):
        start = i
        while stack and stack[-1][1] > height:
            index, h = stack.pop()
            max_area = max(max_area, h * (i-index))
            start = index
        stack.append((start,height))
    while stack:
        index, h = stack.pop()
        max_area = max(max_area, h * (n-index))
    return max_area

heights1 = [2, 1, 5, 6, 2, 3]
print(largest_area_histogram(heights1)) 
