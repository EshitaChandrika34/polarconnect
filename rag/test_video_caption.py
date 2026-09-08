import os
import cv2
from PIL import Image
from transformers import pipeline

VIDEO_PATH = "rag/data/sample.mp4"
OUTPUT_FOLDER = "rag/data/extracted_frames"

print("Loading image captioning model...")

captioner = pipeline(
    "image-text-to-text",
    model="Salesforce/blip-image-captioning-base"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Extract 5 frames evenly
frame_positions = [
    int(total_frames * i / 5)
    for i in range(5)
]

print("\nProcessing video frames...\n")

for i, frame_position in enumerate(frame_positions):

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
    success, frame = cap.read()

    if success:
        frame_path = os.path.join(
            OUTPUT_FOLDER,
            f"caption_frame_{i}.jpg"
        )

        cv2.imwrite(frame_path, frame)

        image = Image.open(frame_path)

        result = captioner(image)

        print(f"Frame {i}")
        print("Description:", result[0]["generated_text"])
        print("-" * 50)

cap.release()

print("\nVideo processing completed!")