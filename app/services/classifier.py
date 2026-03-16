from enum import Enum
from typing import Tuple


class ExposureCondition(str, Enum):
    UNDEREXPOSED = "UNDEREXPOSED"
    OVEREXPOSED = "OVEREXPOSED"
    LOW_CONTRAST = "LOW_CONTRAST"
    NORMAL = "NORMAL"


class Severity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


# Maps each condition to the enhancement method name
METHOD_MAP = {
    ExposureCondition.UNDEREXPOSED: "gamma_correction",
    ExposureCondition.OVEREXPOSED: "tone_compression",
    ExposureCondition.LOW_CONTRAST: "clahe",
    ExposureCondition.NORMAL: "passthrough",
}


def classify(mean: float, std: float) -> ExposureCondition:
    """
    Classify exposure condition based on L-channel stats.
    Thresholds tuned for 0-255 L-channel values.
    """
    if mean < 95:
        return ExposureCondition.UNDEREXPOSED
    elif mean > 165:
        return ExposureCondition.OVEREXPOSED
    elif std < 55:
        return ExposureCondition.LOW_CONTRAST
    else:
        return ExposureCondition.NORMAL