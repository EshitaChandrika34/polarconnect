from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

print("Loading image captioning model...")

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

image_path = "rag/data/images/DavidMerronuntitled-51-2.avif"

image = Image.open(image_path).convert("RGB")

print("\nGenerating caption...\n")

inputs = processor(images=image, return_tensors="pt")

output = model.generate(**inputs, max_new_tokens=50)

caption = processor.decode(
    output[0],
    skip_special_tokens=True
)

print("IMAGE DESCRIPTION:")
print(caption)