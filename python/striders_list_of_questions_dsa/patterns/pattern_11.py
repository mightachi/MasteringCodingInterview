def nBinaryTriangle(n: int) -> None:
    # Write your solution here.
    # Loop for each row
    for i in range(1, n + 1):
        # Initialize the starting value for each row
        num = i % 2
        # Loop for each column in the row
        for j in range(i):
            # Print the binary number
            print(num, end=" ")
            # Alternate between 0 and 1 for each column
            num = 1 - num
        # Move to the next line after printing each row
        print()
    pass