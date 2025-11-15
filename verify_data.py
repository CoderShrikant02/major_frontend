import json

# Load and verify the data
with open('pesticide_recommendations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("VERIFICATION OF ALL PESTICIDE RECOMMENDATIONS")
print("="*60)

for disease, recommendations in sorted(data.items()):
    print(f"\n{disease}: {len(recommendations)} recommendations")
    for i, pest in enumerate(recommendations, 1):
        print(f"  {i}. {pest['pesticide_name']}")

print("\n" + "="*60)
print(f"Total diseases: {len(data)}")
print(f"Total recommendations: {sum(len(recs) for recs in data.values())}")
print("="*60)
