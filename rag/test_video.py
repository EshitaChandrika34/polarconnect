import cv2
import os

video_path = "rag/data/videos/test_video.mp4"
output_folder = "rag/data/extracted_frames"

os.makedirs(output_folder, exist_ok=True)

video = cv2.VideoCapture(video_path)

fps = video.get(cv2.CAP_PROP_FPS)
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps if fps > 0 else 0

print(f"FPS: {fps}")
print(f"Total Frames: {frame_count}")
print(f"Duration: {duration:.2f} seconds")

# Extract one frame every 5 seconds
interval = int(fps * 5)

current_frame = 0
saved_count = 0

while True:
    success, frame = video.read()

    if not success:
        break

    if current_frame % interval == 0:
        frame_path = os.path.join(
            output_folder,
            f"frame_{saved_count}.jpg"
        )

        cv2.imwrite(frame_path, frame)
        print(f"Saved: {frame_path}")

        saved_count += 1

    current_frame += 1

video.release()

print(f"\nDone! Extracted {saved_count} frames.")