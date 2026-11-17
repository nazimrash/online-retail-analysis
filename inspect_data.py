from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent
file_path = project_folder / "data" / "raw" / "Online Retail.xlsx"

df = pd.read_excel(file_path)

print("First five rows:")
print(df.head().to_string(index=False))

print("\nRows and columns:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())