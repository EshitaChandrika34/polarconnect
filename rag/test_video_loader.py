from src.video_loader import load_video


video_path = "rag/data/videos/test_video.mp4"

result = load_video(video_path)

print("\nFINAL VIDEO DESCRIPTION:")
print(result)