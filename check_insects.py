import pandas as pd

# Read the insects responsible file
df = pd.read_excel('insects responsible.xlsx')
df.columns = df.columns.str.strip()

print("Disease to Responsible Pest Mapping:")
print("="*60)

for idx, row in df.iterrows():
    if not pd.isna(row['Disease']) and not pd.isna(row['Pest Name']):
        print(f"{row['Disease']}: {row['Pest Name']}")
