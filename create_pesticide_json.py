import json

# Manual data creation based on the Excel screenshots
pesticide_data = {
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": [
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Pyron (Vector Control)",
            "ingredients": "Pyriproxyfen 5% and Diafenthiuron 25% SE",
            "quantity": "400 ml per acre",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Antivirus (Virus Control)",
            "ingredients": "",
            "quantity": "500 ml per acre",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Decis",
            "ingredients": "Deltamethrin 2.8% EC",
            "quantity": "1ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Hostathian",
            "ingredients": "Triazophos 40% EC",
            "quantity": "1ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Karate",
            "ingredients": "Lambda-cyhalothrin 5% EC",
            "quantity": "0.5ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Pride/ Rekord",
            "ingredients": "Acetamiprid 20% SP",
            "quantity": "0.2g per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Beauveria Bassiana",
            "ingredients": "",
            "quantity": "1 to 2 liter per acre",
            "type": "BIO",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "White Flies (Bemisia Tabacci)",
            "pesticide_name": "Verticillium lecanii",
            "ingredients": "",
            "quantity": "1 to 2 liter per acre",
            "type": "BIO",
            "disease_type": "Insect Based"
        }
    ],
    "Leaf Miner": [
        {
            "insect_name": "Leaf Miner",
            "pesticide_name": "Kalyayani Demat",
            "ingredients": "Dimethoate 30% EC",
            "quantity": "300 ml per acre",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "Leaf Miner",
            "pesticide_name": "Decis",
            "ingredients": "Deltamethrin 2.8% EC",
            "quantity": "1ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        }
    ],
    "Tomato___Spider_mites Two-spotted_spider_mite": [
        {
            "insect_name": "Spider Mites",
            "pesticide_name": "Omite",
            "ingredients": "Propargite 57% EC",
            "quantity": "2ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        },
        {
            "insect_name": "Spider Mites",
            "pesticide_name": "Vertimec",
            "ingredients": "Abamectin 1.8% EC",
            "quantity": "0.5ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        }
    ],
    "Tomato___Early_blight": [
        {
            "insect_name": "Early Blight Fungus",
            "pesticide_name": "Mancozeb",
            "ingredients": "Mancozeb 75% WP",
            "quantity": "2-3g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        },
        {
            "insect_name": "Early Blight Fungus",
            "pesticide_name": "Chlorothalonil",
            "ingredients": "Chlorothalonil 75% WP",
            "quantity": "2g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        }
    ],
    "Tomato___Late_blight": [
        {
            "insect_name": "Late Blight Fungus",
            "pesticide_name": "Ridomil Gold",
            "ingredients": "Metalaxyl 8% + Mancozeb 64% WP",
            "quantity": "2.5g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        },
        {
            "insect_name": "Late Blight Fungus",
            "pesticide_name": "Curzate",
            "ingredients": "Cymoxanil 8% + Mancozeb 64% WP",
            "quantity": "2g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        }
    ],
    "Tomato___Bacterial_spot": [
        {
            "insect_name": "Bacterial Spot",
            "pesticide_name": "Copper Oxychloride",
            "ingredients": "Copper Oxychloride 50% WP",
            "quantity": "3g per liter",
            "type": "Chemical",
            "disease_type": "Bacterial"
        },
        {
            "insect_name": "Bacterial Spot",
            "pesticide_name": "Streptocycline",
            "ingredients": "Streptomycin Sulphate 90% + Tetracycline 10%",
            "quantity": "0.5g per liter",
            "type": "Chemical",
            "disease_type": "Bacterial"
        }
    ],
    "Tomato___Leaf_Mold": [
        {
            "insect_name": "Leaf Mold Fungus",
            "pesticide_name": "Bavistin",
            "ingredients": "Carbendazim 50% WP",
            "quantity": "1g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        }
    ],
    "Tomato___Septoria_leaf_spot": [
        {
            "insect_name": "Septoria Fungus",
            "pesticide_name": "Mancozeb",
            "ingredients": "Mancozeb 75% WP",
            "quantity": "2-3g per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        }
    ],
    "Tomato___Target_Spot": [
        {
            "insect_name": "Target Spot Fungus",
            "pesticide_name": "Azoxystrobin",
            "ingredients": "Azoxystrobin 23% SC",
            "quantity": "1ml per liter",
            "type": "Chemical",
            "disease_type": "Fungal"
        }
    ],
    "Tomato___Tomato_mosaic_virus": [
        {
            "insect_name": "Aphids (Virus Vector)",
            "pesticide_name": "Imidacloprid",
            "ingredients": "Imidacloprid 17.8% SL",
            "quantity": "0.5ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        }
    ],
    "Spotted Wilt Virus": [
        {
            "insect_name": "Thrips (Virus Vector)",
            "pesticide_name": "Fipronil",
            "ingredients": "Fipronil 5% SC",
            "quantity": "2ml per liter",
            "type": "Chemical",
            "disease_type": "Insect Based"
        }
    ],
    "Tomato___healthy": [
        {
            "insect_name": "Prevention",
            "pesticide_name": "Neem Oil",
            "ingredients": "Neem Oil (Organic)",
            "quantity": "5ml per liter",
            "type": "Organic",
            "disease_type": "Preventive"
        },
        {
            "insect_name": "Prevention",
            "pesticide_name": "Trichoderma",
            "ingredients": "Trichoderma viride (Bio-fungicide)",
            "quantity": "5g per liter",
            "type": "BIO",
            "disease_type": "Preventive"
        }
    ]
}

# Save to JSON file
with open('pesticide_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(pesticide_data, f, indent=2, ensure_ascii=False)

print("✅ Pesticide recommendations saved to pesticide_recommendations.json")
print(f"📊 Total diseases covered: {len(pesticide_data)}")
for disease, pesticides in pesticide_data.items():
    print(f"   - {disease}: {len(pesticides)} recommendations")
