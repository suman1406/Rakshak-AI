import os
import cv2
import numpy as np
import pytest
from app.modules.processing.extractor import VideoFrameExtractor

def generate_synthetic_video(output_path: str, num_frames: int = 15, width: int = 128, height: int = 128, fps: float = 5.0):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for i in range(num_frames):
        frame = np.full((height, width, 3), (i * 15) % 255, dtype=np.uint8)
        out.write(frame)
    out.release()

def test_video_frame_extractor(tmp_path):
    video_file = str(tmp_path / "test_sample.mp4")
    frames_dir = str(tmp_path / "extracted_frames")
    
    generate_synthetic_video(video_file, num_frames=15, fps=5.0)
    
    extractor = VideoFrameExtractor(target_fps=2.0, max_frames=20)
    extracted = extractor.extract_frames(video_file, frames_dir)

    assert len(extracted) > 0
    assert os.path.exists(frames_dir)
    assert os.path.exists(extracted[0].file_path)
    assert extracted[0].image is not None
    assert extracted[0].sequence_index == 0
