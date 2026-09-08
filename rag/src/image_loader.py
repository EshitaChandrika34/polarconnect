from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

_processor = None
_model = None


def load_caption_model():
    global _processor, _model

    if _processor is None or _model is None:
        print("Loading image captioning model...")

        _processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

        _model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

    return _processor, _model


def load_image(image_path):
    """
    Generates a text description for an image.
    """

    try:
        image = Image.open(image_path).convert("RGB")

        processor, model = load_caption_model()

        # Process image
        inputs = processor(images=image, return_tensors="pt")

        # Generate caption
        output = model.generate(**inputs, max_new_tokens=50)

        # Decode caption
        caption = processor.decode(
            output[0],
            skip_special_tokens=True
        )

        print(f"Image caption generated: {caption}")

        return caption

    except Exception as e:
        print(f"Error processing image: {e}")
        return None