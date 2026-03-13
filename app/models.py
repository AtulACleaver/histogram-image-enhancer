from pydantic import BaseModel
from typing import List, Optional

class EnhanceResponse(BaseModel):
    condition: str
    method: str
    original_histogram: List[int]
    enhanced_histogram: List[int]
    original_mean: float
    original_std: float
    enhanced_mean: float
    enhanced_std: float
    message: str