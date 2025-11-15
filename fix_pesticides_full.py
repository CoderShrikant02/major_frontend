import pandas as pd
import json

# Read the Excel file with all pesticide data
df = pd.read_excel('disease and pesticides.xlsx')

# Print total rows for debugging
print(f"Total rows in Excel: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}\n")

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Create dictionary to store recommendations
pesticide_data = {}

# Process each row
for index, row in df.iterrows():
    # Get disease name and clean it
    disease = str(row['DISEASE']).strip() if not pd.isna(row['DISEASE']) else ""
    
    # Skip if disease is empty
    if disease == '' or disease == 'nan':
        print(f"Skipping row {index+2}: Empty disease")
        continue
    
    # Initialize list for this disease if not exists
    if disease not in pesticide_data:
        pesticide_data[disease] = []
    
    # Get all fields
    insect_name = str(row['INSECT_NAME / ORGANISM NAME']).strip() if not pd.isna(row['INSECT_NAME / ORGANISM NAME']) else ""
    pesticide_name = str(row['PESTICIDE_NAME']).strip() if not pd.isna(row['PESTICIDE_NAME']) else ""
    ingredients = str(row['INGRIDENTS']).strip() if not pd.isna(row['INGRIDENTS']) else ""
    quantity = str(row['QUANTITY']).strip() if not pd.isna(row['QUANTITY']) else ""
    
    # Get type from Excel or determine it
    if 'TYPE OF INSECTICIDE / FUNGICIDE' in df.columns and not pd.isna(row['TYPE OF INSECTICIDE / FUNGICIDE']):
        pesticide_type = str(row['TYPE OF INSECTICIDE / FUNGICIDE']).strip()
    else:
        pesticide_type = "Chemical"
        if "BIO" in pesticide_name.upper() or "BEAUVERIA" in pesticide_name.upper() or "VERTICILLIUM" in pesticide_name.upper() or "TRICHODERMA" in pesticide_name.upper():
            pesticide_type = "BIO"
        elif "NEEM" in pesticide_name.upper() or "ORGANIC" in ingredients.upper():
            pesticide_type = "Organic"
    
    # Get disease type from Excel or determine it
    if 'TYPE OF DISEASE' in df.columns and not pd.isna(row['TYPE OF DISEASE']):
        disease_type = str(row['TYPE OF DISEASE']).strip()
    else:
        disease_type = "Insect Based"
        if "fungus" in insect_name.lower() or "blight" in disease.lower() or "mold" in disease.lower() or "spot" in disease.lower():
            disease_type = "Fungal"
        elif "bacteria" in insect_name.lower() or "bacterial" in disease.lower():
            disease_type = "Bacterial"
        elif "prevention" in insect_name.lower() or "healthy" in disease.lower():
            disease_type = "Preventive"
    
    # Create pesticide entry
    pesticide_entry = {
        "insect_name": insect_name,
        "pesticide_name": pesticide_name,
        "ingredients": ingredients,
        "quantity": quantity,
        "type": pesticide_type,
        "disease_type": disease_type
    }
    
    # Add to list
    pesticide_data[disease].append(pesticide_entry)
    print(f"Row {index+2}: Added {pesticide_name} for {disease}")

# Print summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for disease, recommendations in sorted(pesticide_data.items()):
    print(f"{disease}: {len(recommendations)} recommendations")

print(f"\nTotal diseases: {len(pesticide_data)}")
print(f"Total recommendations: {sum(len(recs) for recs in pesticide_data.values())}")

# Save to JSON file
with open('pesticide_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(pesticide_data, f, indent=2, ensure_ascii=False)

print("\n✓ Successfully created pesticide_recommendations.json with ALL data!")
