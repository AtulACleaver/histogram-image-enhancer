import cv2
import numpy as np

TARGET_MEAN = 128.0  # Neutral midtone target (midpoint of 0-255 scale)


def _adaptive_gamma_for_underexposure(mean: float) -> float:
    """
    Compute a gamma value that maps the current mean toward TARGET_MEAN.
    Uses the log-ratio formula: gamma = log(target/255) / log(mean/255)
    Clamped to [0.15, 0.70] to prevent extreme over-brightening.
    """
    if mean <= 0:
        return 0.15
    gamma = np.log(TARGET_MEAN / 255.0) / np.log(mean / 255.0)
    return float(np.clip(gamma, 0.15, 0.70))


def _adaptive_gamma_for_overexposure(mean: float) -> float:
    """
    Compute a gamma > 1 that maps the current mean toward TARGET_MEAN.
    Clamped to [1.30, 2.50] to prevent over-darkening.
    """
    if mean >= 255:
        return 2.50
    gamma = np.log(TARGET_MEAN / 255.0) / np.log(mean / 255.0)
    return float(np.clip(gamma, 1.30, 2.50))


def gamma_correct(l_channel: np.ndarray, severity: str = "moderate") -> np.ndarray:
    """
    Brighten underexposed images using an adaptive gamma derived from
    the actual mean intensity, so correction strength scales with how
    dark the image is.

    severity: 'mild' | 'moderate' | 'severe'
    """
    mean = float(np.mean(l_channel))
    gamma = _adaptive_gamma_for_underexposure(mean)

    normalized = l_channel / 255.0
    corrected = np.power(normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


def histogram_equalize(l_channel: np.ndarray, **kwargs) -> np.ndarray:
    """Standard histogram equalization. Spreads out intensity distribution."""
    return cv2.equalizeHist(l_channel)


def clahe_enhance(l_channel: np.ndarray, severity: str = "moderate") -> np.ndarray:
    """
    Contrast Limited Adaptive Histogram Equalization.
    clip_limit and tileGridSize scale with severity to avoid either
    under-correcting flat images or amplifying noise in mild cases.

    severity: 'mild' | 'moderate' | 'severe'
    """
    clip_limits = {"mild": 3.0, "moderate": 4.5, "severe": 6.0}
    grid_sizes  = {"mild": 8,   "moderate": 6,   "severe": 4}

    clip_limit = clip_limits.get(severity, 4.5)
    grid_size  = grid_sizes.get(severity, 6)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(grid_size, grid_size),
    )
    return clahe.apply(l_channel)


def tone_compress(l_channel: np.ndarray, severity: str = "moderate") -> np.ndarray:
    """
    Reduce brightness in overexposed images using an adaptive gamma
    derived from the actual mean intensity.

    severity: 'mild' | 'moderate' | 'severe'
    """
    mean = float(np.mean(l_channel))
    gamma = _adaptive_gamma_for_overexposure(mean)

    normalized = l_channel / 255.0
    corrected = np.power(normalized, gamma)
    return np.clip(corrected * 255, 0, 255).astype(np.uint8)


def passthrough(l_channel: np.ndarray, **kwargs) -> np.ndarray:
    """No enhancement needed. Return as-is."""
    return l_channel


# Strategy map: method name -> enhancement function
ENHANCE_FUNCTIONS = {
    "gamma_correction":   gamma_correct,
    "tone_compression":   tone_compress,
    "clahe":              clahe_enhance,
    "histogram_equalize": histogram_equalize,
    "passthrough":        passthrough,
}