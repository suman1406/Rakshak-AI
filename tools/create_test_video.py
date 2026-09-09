#!/usr/bin/env python3
"""
create_test_video.py — Synthesize Authentic Leaf Test Video Fixture

Stitches authentic leaf images from model/dataset_split into an MP4 video fixture.
Ensures valid duration (>10s) and frame rate (5 FPS) conforming to Rakshak AI's
video ingestion requirements.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import cv2


def create_video_from_images(
    images_dir: Path,
    output_path: Path,
    num_frames: int = 55,
    fps: float = 5.0,
    target_size: tuple[int, int] = (512, 512),
) -> Path:
    if not images_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {images_dir}")

    image_paths = sorted(
        [p for p in images_dir.glob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    )
    if not image_paths:
        raise ValueError(f"No image files found in {images_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, target_size)

    try:
        written_count = 0
        for i in range(num_frames):
            img_path = image_paths[i % len(image_paths)]
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
            out.write(resized)
            written_count += 1

        if written_count == 0:
            raise RuntimeError("Failed to write any frames to the video.")
    finally:
        out.release()

    duration = written_count / fps
    print(f"✅ Generated test video: {output_path}")
    print(f"   Frames: {written_count} | FPS: {fps} | Duration: {duration:.1f}s | Size: {output_path.stat().st_size / 1024:.1f} KB")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Create authentic leaf test MP4 video from dataset images.")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="model/dataset_split/test/soybean_rust",
        help="Path to folder of leaf images",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tools/soybean_rust_test.mp4",
        help="Output MP4 file path",
    )
    parser.add_argument("--num-frames", type=int, default=55, help="Number of frames (default 55 = 11s @ 5fps)")
    parser.add_argument("--fps", type=float, default=5.0, help="Framerate in FPS (default 5.0)")
    parser.add_argument("--width", type=int, default=512, help="Target frame width (default 512)")
    parser.add_argument("--height", type=int, default=512, help="Target frame height (default 512)")

    args = parser.parse_args()
    input_path = Path(args.input_dir)
    output_path = Path(args.output)

    create_video_from_images(
        images_dir=input_path,
        output_path=output_path,
        num_frames=args.num_frames,
        fps=args.fps,
        target_size=(args.width, args.height),
    )


if __name__ == "__main__":
    main()
