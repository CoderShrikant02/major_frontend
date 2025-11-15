from PIL import Image, ImageDraw, ImageFont
import os

# Create pest_images directory if it doesn't exist
os.makedirs('static/pest_images', exist_ok=True)

# Pest information with colors
pests = {
    'whitefly.jpg': ('White Fly', (255, 255, 200)),
    'leafminer.jpg': ('Leaf Miner', (100, 150, 50)),
    'thrips.jpg': ('Thrips', (200, 150, 100)),
    'spider_mite.jpg': ('Spider Mite', (200, 100, 100)),
    'phytophthora.jpg': ('Phytophthora', (150, 100, 150)),
    'alternaria.jpg': ('Alternaria', (100, 100, 100)),
    'xanthomonas.jpg': ('Xanthomonas', (150, 150, 200))
}

for filename, (name, color) in pests.items():
    # Create a 200x200 image
    img = Image.new('RGB', (200, 200), color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    draw.ellipse([50, 50, 150, 150], fill=(min(color[0]+50, 255), min(color[1]+50, 255), min(color[2]+50, 255)), outline=(255, 255, 255), width=3)
    
    # Add text
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Draw text at bottom
    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (200 - text_width) // 2
    draw.text((text_x, 160), name, fill=(255, 255, 255), font=font)
    
    # Save the image
    filepath = os.path.join('static', 'pest_images', filename)
    img.save(filepath)
    print(f"✓ Created {filepath}")

print(f"\n✓ Created {len(pests)} placeholder pest images")
print("\nYou can replace these with actual pest photos later!")
print("Just place real images in: static/pest_images/")
