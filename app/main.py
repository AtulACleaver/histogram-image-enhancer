import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import cv2
import numpy as np
from app.models import EnhanceResponse

app = FastAPI(
    title="Histogram Image Enhancer",
    description="Upload an image, get back an auto-enhanced version with metadata.",
    version="1.0.0",
)

ALLOWED_TYPES = ["image/jpeg", "image/png"]
MAX_SIZE_MB = 10
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: JPEG, PNG.",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_SIZE_MB}MB.",
        )

    # Decode to NumPy array
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    # PLACEHOLDER - will be replaced in Block 3
    return {
        "condition": "PLACEHOLDER",
        "method": "none",
        "message": "Upload works. Processing not wired yet.",
        "image_shape": list(img.shape),
    }