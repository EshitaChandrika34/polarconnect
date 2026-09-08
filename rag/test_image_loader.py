from src.image_loader import load_image

image_path = "rag/data/images/DavidMerronuntitled-51-2.avif"

caption = load_image(image_path)

print("\nFINAL CAPTION:")
print(caption)