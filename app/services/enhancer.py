import cv2
import numpy as np


def gamma_correct(l_channel: np.ndarray, gamma: float = 0.4) -> np.ndarray:
    """
    Brighten underexposed images.
    gamma < 1 brightens, gamma > 1 darkens.
    """
    # Normalize to 0-1, apply gamma, scale back
    normalized = l_channel / 255.0
    corrected = np.power(normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


def histogram_equalize(l_channel: np.ndarray) -> np.ndarray:
    """Standard histogram equalization. Spreads out intensity distribution."""
    return cv2.equalizeHist(l_channel)


def clahe_enhance(l_channel: np.ndarray, clip_limit: float = 2.0, grid_size: int = 8) -> np.ndarray:
    """
    Contrast Limited Adaptive Histogram Equalization.
    Better than full equalization for low-contrast images - avoids over-amplifying noise.
    """
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit, tileGridSize=(grid_size, grid_size)
    )
    return clahe.apply(l_channel)


def tone_compress(l_channel: np.ndarray, gamma: float = 1.8) -> np.ndarray:
    """
    Reduce brightness in overexposed images.
    gamma > 1 darkens the image.
    """
    normalized = l_channel / 255.0
    corrected = np.power(normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


def passthrough(l_channel: np.ndarray) -> np.ndarray:
    """No enhancement needed. Return as-is."""
    return l_channel


# Strategy map: condition -> enhancement function
ENHANCE_FUNCTIONS = {
    "gamma_correction": gamma_correct,
    "tone_compression": tone_compress,
    "clahe": clahe_enhance,
    "histogram_equalize": histogram_equalize,
    "passthrough": passthrough,
}