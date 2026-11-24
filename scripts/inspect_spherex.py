import pandas as pd

file_path = "data/spherex_search_results.csv"

df = pd.read_csv(file_path)

print("\nCOSMIC ECHO | DATASET INSPECTION")
print("=" * 45)

print("\nTotal records:", len(df))

print("\nAvailable columns:")
for column in df.columns:
    print("-", column)

print("\nFirst 5 records:")
print(df.head().to_string())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())