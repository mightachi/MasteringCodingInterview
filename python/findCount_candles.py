'''


Need to return the maximum group of the candles
conditions:
each group must have 3 candles and no two candle can have the same color
each candle would belong to a single group

sample input:
N=12
A = [1,2,3,3,2,1,1,2,3,3,3,3]
output:3

'''
# def find_count(N,A):
def max_candle_groups(n, colors):
    from collections import Counter
    
    # Count the occurrences of each color
    color_counts = Counter(colors)
    
    # Get the counts of each color
    counts = list(color_counts.values())
    
    # Sort counts in descending order
    counts.sort(reverse=True)
    
    groups = 0
    
    # Form groups of 3 as long as we have at least 3 different colors
    while len(counts) >= 3:
        # Create a group of the top 3 colors
        groups += 1
        counts[0] -= 1  # Using one candle from the color with max count
        counts[1] -= 1  # Using one candle from the second color
        counts[2] -= 1  # Using one candle from the third color
        
        # Remove colors that have count reduced to zero
        counts = [count for count in counts if count > 0]
        
        # Sort again to maintain the order
        counts.sort(reverse=True)
        
    return groups


# Example usage
n=10
colors = [87, 23, 1, 89, 3, 11, 90, 21]
result = max_candle_groups(n,colors)
print(result)  # Output: 8

n=12
colors = [1,2,3,3,2,1,1,2,3,3,3,3]
result = max_candle_groups(n,colors)
print(result)