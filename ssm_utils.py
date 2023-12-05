"""Helpful tools for generating self-similarity matrices"""

import numpy as np

def boundary_split(array, indices) :
  """chatgpt-generated"""
  # Check if the indices are valid
  if any(index < 0 or index >= len(array) for index in indices):
    raise ValueError("Invalid index in the list.")

  # Add the start and end indices to the list
  split_indices = [0] + sorted(indices) + [len(array)]

  # Create subarrays using slicing
  subarrays = [
    array[int(split_indices[i]) : int(split_indices[i + 1])] 
    for i in range(len(split_indices) - 1)
  ]

  return subarrays
