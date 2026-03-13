import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import cv2
import numpy as np

from app.services.histogram import (
    extract_histogram,
    compute_stats,
    get_lightness_channel,
    merge_lightness,
)
from app.services.classifier import classify, METHOD_MAP
from app.services.enhancer import ENHANCE_FUNCTIONS

app = FastAPI(
    title="Histogram Image Enhancer",
    description="Upload an image. Get back an auto-enhanced version with metadata about what was detected and fixed.",
    version="1.0.0",
)

ALLOWED_TYPES = ["image/jpeg", "image/png"]
MAX_SIZE_MB = 10
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/health", tags=["System"])
def health_check():
    """Check if the API is running."""
    return {"status": "ok"}


@app.post("/enhance", tags=["Enhancement"])
async def enhance_image(file: UploadFile = File(..., description="JPEG or PNG image to enhance")):
    """
    Upload an image to auto-detect exposure issues and apply the best enhancement.

    Returns the enhanced image as a file download.
    Metadata is included in response headers:
    - X-Condition: detected exposure condition
    - X-Method: enhancement method applied
    - X-Original-Mean / X-Original-Std: original L-channel stats
    - X-Enhanced-Mean / X-Enhanced-Std: enhanced L-channel stats
    """
    # --- Validate ---
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: JPEG, PNG.",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {MAX_SIZE_MB}MB.")

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    # --- Analyze ---
    l_channel, lab_image = get_lightness_channel(img)
    original_hist = extract_histogram(l_channel)
    orig_mean, orig_std = compute_stats(l_channel)

    # --- Classify ---
    condition = classify(orig_mean, orig_std)
    method_name = METHOD_MAP[condition]

    # --- Enhance ---
    enhance_fn = ENHANCE_FUNCTIONS[method_name]
    enhanced_l = enhance_fn(l_channel)
    enhanced_img = merge_lightness(lab_image.copy(), enhanced_l)

    # --- Post-analysis ---
    enhanced_hist = extract_histogram(enhanced_l)
    enh_mean, enh_std = compute_stats(enhanced_l)

    # --- Save outputs ---
    file_id = str(uuid.uuid4())[:8]
    ext = ".png" if file.content_type == "image/png" else ".jpg"
    original_path = os.path.join(OUTPUT_DIR, f"{file_id}_original{ext}")
    enhanced_path = os.path.join(OUTPUT_DIR, f"{file_id}_enhanced{ext}")

    cv2.imwrite(original_path, img)
    cv2.imwrite(enhanced_path, enhanced_img)

    # --- Return enhanced image with metadata in headers ---
    return FileResponse(
        path=enhanced_path,
        media_type=file.content_type,
        filename=f"enhanced_{file_id}{ext}",
        headers={
            "X-Condition": condition.value,
            "X-Method": method_name,
            "X-Original-Mean": f"{orig_mean:.2f}",
            "X-Original-Std": f"{orig_std:.2f}",
            "X-Enhanced-Mean": f"{enh_mean:.2f}",
            "X-Enhanced-Std": f"{enh_std:.2f}",
        },
    )


@app.post("/enhance/json", tags=["Enhancement"])
async def enhance_image_json(file: UploadFile = File(..., description="JPEG or PNG image to enhance")):
    """
    Same as /enhance but returns JSON metadata instead of the image file.
    Use this to inspect the analysis without downloading the image.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}. Allowed: JPEG, PNG.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {MAX_SIZE_MB}MB.")

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    l_channel, lab_image = get_lightness_channel(img)
    original_hist = extract_histogram(l_channel)
    orig_mean, orig_std = compute_stats(l_channel)

    condition = classify(orig_mean, orig_std)
    method_name = METHOD_MAP[condition]

    enhance_fn = ENHANCE_FUNCTIONS[method_name]
    enhanced_l = enhance_fn(l_channel)
    enhanced_img = merge_lightness(lab_image.copy(), enhanced_l)

    enhanced_hist = extract_histogram(enhanced_l)
    enh_mean, enh_std = compute_stats(enhanced_l)

    file_id = str(uuid.uuid4())[:8]
    ext = ".png" if file.content_type == "image/png" else ".jpg"
    original_path = os.path.join(OUTPUT_DIR, f"{file_id}_original{ext}")
    enhanced_path = os.path.join(OUTPUT_DIR, f"{file_id}_enhanced{ext}")
    cv2.imwrite(original_path, img)
    cv2.imwrite(enhanced_path, enhanced_img)

    return {
        "condition": condition.value,
        "method": method_name,
        "original_mean": round(orig_mean, 2),
        "original_std": round(orig_std, 2),
        "enhanced_mean": round(enh_mean, 2),
        "enhanced_std": round(enh_std, 2),
        "original_histogram": original_hist.tolist(),
        "enhanced_histogram": enhanced_hist.tolist(),
        "files": {
            "original": original_path,
            "enhanced": enhanced_path,
        },
        "message": f"Detected {condition.value}. Applied {method_name}.",
    }