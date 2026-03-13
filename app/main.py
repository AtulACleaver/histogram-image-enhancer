from fastapi import FastAPI

app = FastAPI(
    title="Histogram Image Enhancer",
    description="Upload an image, get back an auto-enhanced version with metadata.",
    version="1.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}