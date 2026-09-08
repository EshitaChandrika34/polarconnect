import cv2
import os

from src.image_loader import load_image


def load_video(video_path, num_frames=5):
    """
    Extract frames from a video and generate
    captions for selected frames.
    """

    try:
        cap = cv2.VideoCapture(video_path)

        total_frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        if total_frames == 0:
            print("Could not read video.")
            return None

        print(f"Processing video with {total_frames} frames...")

        # Select evenly spaced frames
        frame_positions = [
            int(i * (total_frames - 1) / (num_frames - 1))
            for i in range(num_frames)
        ]

        captions = []

        os.makedirs(
            "rag/data/temp_frames",
            exist_ok=True
        )

        for i, frame_number in enumerate(frame_positions):

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                frame_number
            )

            success, frame = cap.read()

            if success:

                frame_path = (
                    f"rag/data/temp_frames/frame_{i}.jpg"
                )

                cv2.imwrite(frame_path, frame)

                print(
                    f"Generating caption for frame {i + 1}..."
                )

                caption = load_image(frame_path)

                if caption:
                    captions.append(
                        f"Frame {i + 1}: {caption}"
                    )

        cap.release()

        if captions:
            return "\n".join(captions)

        return None

    except Exception as e:
        print(f"Error processing video: {e}")
        return None