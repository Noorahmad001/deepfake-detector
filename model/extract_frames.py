import cv2
import os

# ─── Config ───────────────────────────────────────────────────────────────────
CELEB_DF_PATH = "C:/Users/Noor Ahmad/Downloads/Celeb-DF-v2"  # Change this to where you extracted Celeb-DF
DATASET_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset")

# How many frames to extract per video
FRAMES_PER_VIDEO = 20

# Split ratios
TRAIN_RATIO = 0.7   # 70% for training
VAL_RATIO = 0.15    # 15% for validation
TEST_RATIO = 0.15   # 15% for testing

def extract_frames_from_video(video_path, output_folder, max_frames=20):
    """
    Extracts frames from a video and saves them as images.
    """
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open: {video_path}")
        return 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // max_frames)

    saved = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % interval == 0 and saved < max_frames:
            frame_filename = f"frame_{frame_count:04d}.jpg"
            frame_path = os.path.join(output_folder, frame_filename)
            cv2.imwrite(frame_path, frame)
            saved += 1

        frame_count += 1

    cap.release()
    return saved


def process_all_videos():
    """
    Processes all videos from Celeb-DF and organizes into train/val/test.
    """
    # Source folders
    real_folders = [
        os.path.join(CELEB_DF_PATH, "Celeb-real"),
        os.path.join(CELEB_DF_PATH, "YouTube-real")
    ]
    fake_folders = [
        os.path.join(CELEB_DF_PATH, "Celeb-synthesis")
    ]

    def get_all_videos(folders):
        videos = []
        for folder in folders:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.endswith(('.mp4', '.avi', '.mov')):
                        videos.append(os.path.join(folder, f))
        return videos

    real_videos = get_all_videos(real_folders)
    fake_videos = get_all_videos(fake_folders)

    print(f"📹 Found {len(real_videos)} real videos")
    print(f"📹 Found {len(fake_videos)} fake videos")

    def split_videos(videos):
        total = len(videos)
        train_end = int(total * TRAIN_RATIO)
        val_end = int(total * (TRAIN_RATIO + VAL_RATIO))
        return (
            videos[:train_end],
            videos[train_end:val_end],
            videos[val_end:]
        )

    real_train, real_val, real_test = split_videos(real_videos)
    fake_train, fake_val, fake_test = split_videos(fake_videos)

    splits = {
        "train": {"real": real_train, "fake": fake_train},
        "val":   {"real": real_val,   "fake": fake_val},
        "test":  {"real": real_test,  "fake": fake_test}
    }

    for split_name, categories in splits.items():
        for category, videos in categories.items():
            print(f"\n📂 Processing {split_name}/{category} ({len(videos)} videos)")

            for idx, video_path in enumerate(videos):
                video_name = os.path.splitext(
                    os.path.basename(video_path)
                )[0]

                output_folder = os.path.join(
                    DATASET_OUTPUT,
                    split_name,
                    category,
                    video_name
                )

                saved = extract_frames_from_video(
                    video_path,
                    output_folder,
                    FRAMES_PER_VIDEO
                )

                print(f"  ✅ {idx+1}/{len(videos)} {video_name}: {saved} frames")

    print("\n🎉 Frame extraction complete!")
    print(f"✅ Dataset saved to: {DATASET_OUTPUT}")


if __name__ == "__main__":
    process_all_videos()