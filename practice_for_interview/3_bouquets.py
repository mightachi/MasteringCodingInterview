def min_days_to_get_bouquet(bloomday, m, k):
    if len(bloomday) < m*k:
        return -1
    low, high = min(bloomday), max(bloomday)
    
    def can_make(day):
        flowers = 0
        bouquet = 0
        for i in range(len(bloomday)):
            if bloomday[i] <= day:
                flowers+=1
                if flowers == k:
                    bouquet+=1
                    flowers = 0
            else:
                flowers = 0
        
        return bouquet>=m

    while low<=high:
        mid = (low+high)//2
        if can_make(mid):
            high = mid-1
        else:
            low = mid+1
    
    return low

bloomday = [1,2,3,4,5,6]
m = 3
k = 2

print(min_days_to_get_bouquet(bloomday, m, k))

