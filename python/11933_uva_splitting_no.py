n=-1
input_num = list()
while True:
    n = int(input().strip())
    if n!=0:
        input_num.append(n)
    else:
        break

def split_number(num):
    binary_num_str = bin(num)[2:]
    n = len(binary_num_str)
    ones_indices = [0]*(n+1)
    a = ['0']*(n)
    b = ['0']*(n)
    cnt=1
    for i in range(n-1,-1,-1):
        if binary_num_str[i]=='1':
            ones_indices[cnt]=n-i-1
            cnt+=1

    for i in range(1,cnt):
        if i%2==0:
            b[n-ones_indices[i]-1]='1'
        elif i%2==1:
            a[n-ones_indices[i]-1]='1'
    a=''.join(a)
    b=''.join(b)
    return int(a,2),int(b,2)

for num in input_num:
    a,b = split_number(num)
    print(a,end=" ")   
    print(b) 

