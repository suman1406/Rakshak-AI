from dataclasses import dataclass
import cv2
import numpy as np
import pytest
from app.modules.processing.quality import QualityFilterService

@dataclass
class MockFrame:
    sequence_index: int
    file_path: str
    image: np.ndarray

def create_sharp_image(width=128, height=128):
    # High frequency checkerboard pattern with sharp edges
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if (x // 8 + y // 8) % 2 == 0:
                img[y:y+8, x:x+8] = [255, 255, 255]
    return img

def create_blurry_image(width=128, height=128):
    sharp = create_sharp_image(width, height)
    return cv2.GaussianBlur(sharp, (31, 31), 15.0)

def create_dark_image(width=128, height=128):
    return np.full((height, width, 3), 10, dtype=np.uint8)

def create_overexposed_image(width=128, height=128):
    return np.full((height, width, 3), 245, dtype=np.uint8)

def test_blur_scoring():
    service = QualityFilterService(min_blur_threshold=60.0)
    sharp = create_sharp_image()
    blurry = create_blurry_image()

    sharp_blur = service.compute_blur_score(sharp)
    blurry_blur = service.compute_blur_score(blurry)

    assert sharp_blur > blurry_blur
    assert blurry_blur < 60.0
    assert sharp_blur > 100.0

def test_exposure_scoring():
    service = QualityFilterService()
    normal = np.full((128, 128, 3), 128, dtype=np.uint8)
    dark = create_dark_image()
    overexposed = create_overexposed_image()

    score_normal = service.compute_exposure_score(normal)
    score_dark = service.compute_exposure_score(dark)
    score_overexposed = service.compute_exposure_score(overexposed)

    assert score_normal == 100.0
    assert score_dark < 40.0
    assert score_overexposed < 40.0

def test_near_duplicate_detection():
    service = QualityFilterService(near_dup_diff_threshold=8.0)
    img1 = create_sharp_image()
    img2 = img1.copy()
    img3 = np.full((128, 128, 3), 200, dtype=np.uint8)

    diff_same = service.compute_image_difference(img1, img2)
    diff_different = service.compute_image_difference(img1, img3)

    assert diff_same == 0.0
    assert diff_different > 10.0

def test_quality_filter_evaluation():
    service = QualityFilterService(min_blur_threshold=60.0, min_exposure_score=40.0)
    
    frames = [
        MockFrame(0, "f0.jpg", create_sharp_image()),
        MockFrame(1, "f1.jpg", create_sharp_image()),  # Duplicate of f0
        MockFrame(2, "f2.jpg", create_blurry_image()), # Blurry
        MockFrame(3, "f3.jpg", create_dark_image()),   # Dark
        MockFrame(4, "f4.jpg", np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)), # Usable
    ]

    results, usable_count, avg_quality = service.evaluate_and_filter_frames(frames)
    
    assert len(results) == 5
    assert usable_count >= 2
    assert results[0].is_usable is True
    assert results[0].is_selected is True
    assert results[1].is_usable is True
    assert results[1].is_selected is False  # Pruned as near-dup
    assert results[2].is_usable is False   # Blurry
    assert results[3].is_usable is False   # Dark
