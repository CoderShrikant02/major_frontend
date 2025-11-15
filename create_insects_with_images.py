import json

# Disease to Pest mapping with image file names
responsible_insects = {
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "White Flies (Bemisia Tabacci)",
        "image": "whitefly.png"
    },
    "Leaf Miner": {
        "name": "Leaf Miner",
        "image": "leafminer.jpg"
    },
    "Spotted Wilt Virus": {
        "name": "Thrips",
        "image": "thrips.jpg"
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "name": "Red Spider Mite & Two Spotted Spider Mite",
        "image": "spider_mite.jpg"
    },
    "Tomato___Late_blight": {
        "name": "Phytophthora infestans",
        "image": "phytophthora.jpg"
    },
    "Tomato___Early_blight": {
        "name": "Alternaria solani",
        "image": "alternaria.jpg"
    },
    "Tomato___Bacterial_spot": {
        "name": "Xanthomonas",
        "image": "xanthomonas.jpg"
    }
}

# Save to JSON
with open('responsible_insects.json', 'w', encoding='utf-8') as f:
    json.dump(responsible_insects, f, indent=2, ensure_ascii=False)

print("✓ Created responsible_insects.json with image mappings")
print(f"✓ Total diseases mapped: {len(responsible_insects)}")
print("\nNote: Place pest images in 'static/pest_images/' folder:")
for disease, info in responsible_insects.items():
    print(f"  - {info['image']}")
