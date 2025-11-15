import pandas as pd
import json

# Read the Excel file
df = pd.read_excel('insects responsible.xlsx')

# Print total rows for debugging
print(f"Total rows in Excel: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}\n")

# Create dictionary to store recommendations
pesticide_data = {}

# Process each row
for index, row in df.iterrows():
    # Get disease name and clean it
    disease = str(row['DISEASE']).strip()
    
    # Skip if disease is empty or NaN
    if pd.isna(disease) or disease == '' or disease == 'nan':
        continue
    
    # Initialize list for this disease if not exists
    if disease not in pesticide_data:
        pesticide_data[disease] = []
    
    # Get insect/organism name
    insect_name = str(row['INSECT_NAME / ORGANISM NAME']).strip() if not pd.isna(row['INSECT_NAME / ORGANISM NAME']) else ""
    
    # Get pesticide details
    pesticide_name = str(row['PESTICIDE_NAME']).strip() if not pd.isna(row['PESTICIDE_NAME']) else ""
    ingredients = str(row['INGRIDENTS']).strip() if not pd.isna(row['INGRIDENTS']) else ""
    quantity = str(row['QUANTITY']).strip() if not pd.isna(row['QUANTITY']) else ""
    
    # Determine pesticide type
    pesticide_type = "Chemical"
    if "BIO" in pesticide_name.upper() or "ORGANIC" in ingredients.upper() or insect_name.upper() in ["BEAUVERIA BASSIANA", "VERTICILLIUM LECANII", "TRICHODERMA"]:
        pesticide_type = "BIO"
    elif "NEEM" in pesticide_name.upper() or "NEEM" in ingredients.upper():
        pesticide_type = "Organic"
    
    # Determine disease type
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

# Print summary
print("\n=== SUMMARY ===")
for disease, recommendations in pesticide_data.items():
    print(f"{disease}: {len(recommendations)} recommendations")

print(f"\nTotal diseases: {len(pesticide_data)}")
print(f"Total recommendations: {sum(len(recs) for recs in pesticide_data.values())}")

# Save to JSON file
with open('pesticide_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(pesticide_data, f, indent=2, ensure_ascii=False)

print("\nSuccessfully created pesticide_recommendations.json")
