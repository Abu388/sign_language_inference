#!/usr/bin/env python3
# run_inference.py
import sys
import argparse
from pathlib import Path
from inference import SignLanguageInference

def main():
    parser = argparse.ArgumentParser(description="Sign language inference from video files.")
    parser.add_argument("video", nargs="+", help="Path(s) to video file(s)")
    parser.add_argument("--batch", action="store_true", help="Process multiple videos")
    args = parser.parse_args()

    infer = SignLanguageInference()

    if args.batch or len(args.video) > 1:
        results = infer.predict_batch(args.video)
        for path, cls, conf in results:
            if cls is None:
                print(f"✗ {path} → ERROR: {conf}")
            else:
                print(f"✓ {path} → {cls} (confidence: {conf:.3f})")
    else:
        video_path = args.video[0]
        try:
            cls, conf = infer.predict_video(video_path)
            print(f"Prediction: {cls} (confidence: {conf:.3f})")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()