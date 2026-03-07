import pandas as pd
import os

# Define file names
input_csv = 'large/edubasealldata20260307.csv'
output_parquet = 'data/gias.parquet'

print(f"Reading {input_csv}...")

# 1. Read the CSV
# low_memory=False helps with large files with mixed data types
df = pd.read_csv(input_csv, low_memory=False, encoding='ISO-8859-1')

print("Converting to Parquet with Brotli compression...")

# 2. Convert to Parquet 
# We use 'brotli' or 'snappy' for high compression ratios
df.to_parquet(output_parquet, compression='brotli', index=False)

# 3. Compare Results
original_size = os.path.getsize(input_csv) / (1024 * 1024)
compressed_size = os.path.getsize(output_parquet) / (1024 * 1024)

print(f"--- Done! ---")
print(f"Original CSV Size: {original_size:.2f} MB")
print(f"New Parquet Size: {compressed_size:.2f} MB")
print(f"Reduction: {((original_size - compressed_size) / original_size) * 100:.1f}%")