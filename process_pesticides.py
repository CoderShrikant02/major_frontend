import pandas as pd
import json

# Read the Excel file
df = pd.read_excel('insects responsible.xlsx')

# Create a dictionary to store pesticide recommendations
pesticide_data = {}

# Group by disease name
for disease in df['DISEASE'].unique():
    disease_data = df[df['DISEASE'] == disease]
    
    pesticides = []
    for _, row in disease_data.iterrows():
        pesticide = {
            'insect_name': row['INSECT_NAME / ORGANISM NAME'],
            'pesticide_name': row['PESTICIDE_NAME'],
            'ingredients': row['INGRIDENTS'],
            'quantity': row['QUANTITY'],
            'type': row['TYPE OF INSECTICIDE / FUNGICIDE'],
            'disease_type': row['TYPE OF DISEASE']
        }
        pesticides.append(pesticide)
    
    pesticide_data[disease] = pesticides

# Save to JSON file
with open('pesticide_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(pesticide_data, f, indent=2, ensure_ascii=False)

print("Pesticide recommendations saved to pesticide_recommendations.json")
print(f"Total diseases: {len(pesticide_data)}")
