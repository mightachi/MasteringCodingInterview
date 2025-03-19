def rotate_matrix_clockwise(matrix):
    """
    Rotates a matrix 90 degrees clockwise.

    Args:
        matrix: The input matrix (list of lists).

    Returns:
        The rotated matrix.
    """
    if not matrix or not matrix[0]:  # Handle empty matrix
        return []

    rows = len(matrix)
    cols = len(matrix[0])

    # Transpose the matrix
    print(matrix)
    transposed = [[matrix[j][i] for j in range(rows)] for i in range(cols)]
    print(transposed)

    # Reverse each row to complete the 90-degree clockwise rotation
    rotated = [row[::-1] for row in transposed]

    return rotated

# Example usage
matrix1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
rotated_matrix1 = rotate_matrix_clockwise(matrix1)
print("Rotated Matrix 1:")
for row in rotated_matrix1:
    print(row)

matrix2 = [
    [1, 2],
    [3, 4],
    [5, 6]
]
rotated_matrix2 = rotate_matrix_clockwise(matrix2)
print("\nRotated Matrix 2:")
for row in rotated_matrix2:
    print(row)

matrix3 = []
rotated_matrix3 = rotate_matrix_clockwise(matrix3)
print("\nRotated Matrix 3:")
for row in rotated_matrix3:
    print(row)

matrix4 = [[]]
rotated_matrix4 = rotate_matrix_clockwise(matrix4)
print("\nRotated Matrix 4:")
for row in rotated_matrix4:
    print(row)

matrix5 = [[1]]
rotated_matrix5 = rotate_matrix_clockwise(matrix5)
print("\nRotated Matrix 5:")
for row in rotated_matrix5:
    print(row)