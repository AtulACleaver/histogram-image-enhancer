from enum import Enum


class ExposureCondition(str, Enum):
    UNDEREXPOSED = "UNDEREXPOSED"
    OVEREXPOSED = "OVEREXPOSED"
    LOW_CONTRAST = "LOW_CONTRAST"
    NORMAL = "NORMAL"


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
    if mean < 80:
        return ExposureCondition.UNDEREXPOSED
    elif mean > 180:
        return ExposureCondition.OVEREXPOSED
    elif std < 40:
        return ExposureCondition.LOW_CONTRAST
    else:
        return ExposureCondition.NORMAL