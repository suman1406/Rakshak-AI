from dataclasses import dataclass
import cv2
import numpy as np

@dataclass
class FrameQualityResult:
    sequence_index: int
    file_path: str
    blur_score: float
    exposure_score: float
    composite_quality_score: float
    is_usable: bool
    is_selected: bool
    rejection_reason: str | None = None

class QualityFilterService:
    def __init__(
        self,
        min_blur_threshold: float = 60.0,
        min_exposure_score: float = 40.0,
        near_dup_diff_threshold: float = 8.0,
        max_selected_frames: int = 15,
    ):
        self.min_blur_threshold = min_blur_threshold
        self.min_exposure_score = min_exposure_score
        self.near_dup_diff_threshold = near_dup_diff_threshold
        self.max_selected_frames = max_selected_frames

    def compute_blur_score(self, image: np.ndarray) -> float:
        """
        Computes Variance of Laplacian.
        Higher variance indicates sharper edges; low indicates blur.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())

    def compute_exposure_score(self, image: np.ndarray) -> float:
        """
        Evaluates histogram and mean luminance.
        Returns a score from 0 to 100 (optimal range: mean 90-160).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        mean_val = float(np.mean(gray))
        
        # Penalize underexposure (< 45) and overexposure (> 210)
        if mean_val < 30.0:
            return max(0.0, (mean_val / 30.0) * 35.0)
        elif mean_val > 225.0:
            return max(0.0, ((255.0 - mean_val) / 30.0) * 35.0)
        
        # Bell-curve score centered at 128
        distance_from_center = abs(mean_val - 128.0)
        score = max(0.0, 100.0 - (distance_from_center * 0.7))
        return float(min(100.0, score))

    def compute_image_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Computes normalized mean absolute difference between two 32x32 thumbnails.
        """
        thumb1 = cv2.resize(img1, (32, 32), interpolation=cv2.INTER_AREA)
        thumb2 = cv2.resize(img2, (32, 32), interpolation=cv2.INTER_AREA)
        if len(thumb1.shape) == 3:
            thumb1 = cv2.cvtColor(thumb1, cv2.COLOR_BGR2GRAY)
        if len(thumb2.shape) == 3:
            thumb2 = cv2.cvtColor(thumb2, cv2.COLOR_BGR2GRAY)
        diff = np.mean(np.abs(thumb1.astype(float) - thumb2.astype(float)))
        return float(diff)

    def evaluate_and_filter_frames(
        self,
        frames: list,  # list of ExtractedFrame or objects with sequence_index, file_path, image
    ) -> tuple[list[FrameQualityResult], int, float]:
        """
        Analyzes blur, exposure, and redundancy across frames.
        Returns:
            - results: List of FrameQualityResult for each frame
            - usable_count: Number of usable frames that passed quality checks
            - average_quality: Mean composite quality of usable frames
        """
        results: list[FrameQualityResult] = []
        selected_thumbnails: list[np.ndarray] = []

        for frame in frames:
            img = frame.image
            if img is None and hasattr(frame, "file_path"):
                img = cv2.imread(frame.file_path)
            
            if img is None:
                results.append(
                    FrameQualityResult(
                        sequence_index=frame.sequence_index,
                        file_path=frame.file_path,
                        blur_score=0.0,
                        exposure_score=0.0,
                        composite_quality_score=0.0,
                        is_usable=False,
                        is_selected=False,
                        rejection_reason="Failed to decode image file",
                    )
                )
                continue

            blur = self.compute_blur_score(img)
            exposure = self.compute_exposure_score(img)
            
            # Composite quality metric: 50% normalized blur + 50% exposure
            normalized_blur = min(100.0, (blur / 200.0) * 100.0)
            composite_score = round(0.5 * normalized_blur + 0.5 * exposure, 1)

            is_usable = True
            rejection_reason = None

            if blur < self.min_blur_threshold:
                is_usable = False
                rejection_reason = f"Frame too blurry (blur_score={blur:.1f} < {self.min_blur_threshold})"
            elif exposure < self.min_exposure_score:
                is_usable = False
                rejection_reason = f"Poor exposure (exposure_score={exposure:.1f} < {self.min_exposure_score})"

            is_selected = False
            if is_usable:
                # Check for near-duplicate against previously selected frames
                is_duplicate = False
                for prev_thumb in selected_thumbnails:
                    diff = self.compute_image_difference(img, prev_thumb)
                    if diff < self.near_dup_diff_threshold:
                        is_duplicate = True
                        break

                if not is_duplicate and len(selected_thumbnails) < self.max_selected_frames:
                    is_selected = True
                    thumb = cv2.resize(img, (32, 32))
                    selected_thumbnails.append(thumb)
                elif is_duplicate:
                    rejection_reason = "Pruned as near-duplicate of prior selected frame"

            results.append(
                FrameQualityResult(
                    sequence_index=frame.sequence_index,
                    file_path=frame.file_path,
                    blur_score=round(blur, 2),
                    exposure_score=round(exposure, 2),
                    composite_quality_score=composite_score,
                    is_usable=is_usable,
                    is_selected=is_selected,
                    rejection_reason=rejection_reason,
                )
            )

        usable_frames = [r for r in results if r.is_usable]
        usable_count = len(usable_frames)
        avg_quality = (
            round(sum(r.composite_quality_score for r in usable_frames) / usable_count, 1)
            if usable_count > 0
            else 0.0
        )

        return results, usable_count, avg_quality
