import json

# Manual mapping based on the correct disease to pest relationship
responsible_insects = {
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "White Flies (Bemisia Tabacci)",
    "Leaf Miner": "Leaf Miner",
    "Spotted Wilt Virus": "Thrips",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Red Spider Mite & Two Spotted Spider Mite",
    "Tomato___Late_blight": "Phytophthora infestans",
    "Tomato___Early_blight": "Alternaria solani",
    "Tomato___Bacterial_spot": "Xanthomonas"
}

# Save to JSON file
with open('responsible_insects.json', 'w', encoding='utf-8') as f:
    json.dump(responsible_insects, f, indent=2, ensure_ascii=False)

print("Created responsible_insects.json with correct mapping:")
for disease, pest in responsible_insects.items():
    print(f"  {disease} → {pest}")
