import cv2
import numpy as np
from typing import Tuple


def extract_histogram(gray_image: np.ndarray) -> np.ndarray:
    """Extract 256-bin histogram from a grayscale image."""
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    return hist.flatten().astype(int)


def compute_stats(gray_image: np.ndarray) -> Tuple[float, float]:
    """Return (mean, std_dev) of pixel intensities."""
    mean = float(np.mean(gray_image))
    std = float(np.std(gray_image))
    return mean, std


def get_lightness_channel(bgr_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert BGR to LAB, return (L channel, full LAB image)."""
    lab = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]
    return l_channel, lab


def merge_lightness(lab_image: np.ndarray, new_l: np.ndarray) -> np.ndarray:
    """Replace L channel in LAB image and convert back to BGR."""
    lab_image[:, :, 0] = new_l
    return cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)