import os
from dataclasses import dataclass
from pathlib import Path
import cv2
from ...core.logging import logger

@dataclass
class ExtractedFrame:
    sequence_index: int
    timestamp_ms: float
    file_path: str
    image: any  # numpy ndarray (BGR)

class VideoFrameExtractor:
    def __init__(self, target_fps: float = 1.0, max_frames: int = 30):
        self.target_fps = target_fps
        self.max_frames = max_frames

    def extract_frames(self, video_path: str, output_dir: str) -> list[ExtractedFrame]:
        """
        Extracts frames from video at fixed interval or scene changes.
        Saves extracted frames as JPEG images in output_dir.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {video_path}")
            return []

        native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        
        # Calculate step interval to extract approximately target_fps frames per second
        frame_step = max(1, int(round(native_fps / self.target_fps)))
        
        extracted: list[ExtractedFrame] = []
        frame_idx = 0
        extracted_seq = 0

        while cap.isOpened() and len(extracted) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_step == 0:
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                frame_filename = f"frame_{extracted_seq:04d}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                
                # Write JPEG frame
                cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                
                extracted.append(
                    ExtractedFrame(
                        sequence_index=extracted_seq,
                        timestamp_ms=timestamp_ms,
                        file_path=frame_path,
                        image=frame,
                    )
                )
                extracted_seq += 1

            frame_idx += 1

        cap.release()
        logger.info(
            f"Extracted {len(extracted)} frames from {video_path} (total video frames={total_video_frames}, fps={native_fps:.1f})"
        )
        return extracted
