import numpy as np

# Example 1D array
arr_1d = np.array([1, 2, 3, 4, 5, 6])

# Reshape to a 2D column vector
arr_2d_column_vector = arr_1d.reshape(-1, 1)

print("Original 1D array:")
print(arr_1d)

print("\nReshaped 2D column vector:")
print(arr_2d_column_vector)
