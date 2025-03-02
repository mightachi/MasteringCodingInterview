def max_rectangle_area(arr):
    n = len(arr)
    m = len(arr[0])
    heights = [0]*m
    max_area = 0
    for row in range(n):
        for col in range(m):
            if arr[row][col] == 1:
                heights[col] +=1
            else:
                heights[col] = 0
        max_area = max(max_area, largest_area_histogram(heights))
    return max_area

def largest_area_histogram(heights):
    stack = []
    max_area = 0
    n = len(heights)
    for i, height in enumerate(heights):
        start = i
        while stack and stack[-1][1] > height:
            index,h = stack.pop()
            max_area = max(max_area, h*(i-index))
            start = index
        stack.append((start,height))
    
    for index, h in stack:
        max_area = max(max_area, h * (n-index))
    return max_area

mat = [
        [1, 0, 1, 0, 0], [1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]
]

print(max_rectangle_area(mat))