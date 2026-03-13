# Histogram Image Enhancer

> A FastAPI service that auto-detects image exposure issues and applies the optimal enhancement technique — no manual tuning required.

---

## How It Works

1. **Upload** any JPEG or PNG image (up to 10 MB)
2. **Analyze** — extracts the L channel from LAB color space and computes mean intensity + standard deviation
3. **Classify** the exposure condition:

   | Condition | Criteria | Enhancement Applied |
   |-----------|----------|---------------------|
   | `UNDEREXPOSED` | Low mean intensity | Gamma correction (γ = 0.4) |
   | `OVEREXPOSED` | High mean intensity | Tone compression (γ = 1.8) |
   | `LOW_CONTRAST` | Low standard deviation | CLAHE |
   | `NORMAL` | Within normal range | Passthrough (no change) |

4. **Enhance** only the L (lightness) channel in LAB space — preserves original colors
5. **Return** the enhanced image or JSON metadata

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/histogram-enhancer.git
cd histogram-enhancer

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API Reference

### `GET /health`
Returns the API status.

```json
{ "status": "ok" }
```

---

### `POST /enhance`
Upload an image and receive the **enhanced image file** as a download.

Metadata is returned in the response headers:

| Header | Description |
|--------|-------------|
| `X-Condition` | Detected exposure condition (e.g. `UNDEREXPOSED`) |
| `X-Method` | Enhancement method applied (e.g. `gamma_correction`) |
| `X-Original-Mean` | Mean L-channel value before enhancement |
| `X-Original-Std` | Std deviation of L-channel before enhancement |
| `X-Enhanced-Mean` | Mean L-channel value after enhancement |
| `X-Enhanced-Std` | Std deviation of L-channel after enhancement |

```bash
curl -X POST "http://localhost:8000/enhance" \
  -F "file=@test_images/dark.jpg" \
  --output enhanced.jpg -v
```

---

### `POST /enhance/json`
Same processing pipeline, but returns **JSON metadata** instead of the image file. Useful for inspecting the analysis programmatically.

```bash
curl -X POST "http://localhost:8000/enhance/json" \
  -F "file=@test_images/dark.jpg" | python -m json.tool
```

**Example response:**

```json
{
  "condition": "UNDEREXPOSED",
  "method": "gamma_correction",
  "original_mean": 62.14,
  "original_std": 28.73,
  "enhanced_mean": 141.52,
  "enhanced_std": 49.81,
  "original_histogram": [...],
  "enhanced_histogram": [...],
  "files": {
    "original": "outputs/a3f1bc2d_original.jpg",
    "enhanced": "outputs/a3f1bc2d_enhanced.jpg"
  },
  "message": "Detected UNDEREXPOSED. Applied gamma_correction."
}
```

---

## Project Structure

```
histogram-enhancer/
├── app/
│   ├── main.py               # FastAPI app, route handlers
│   ├── models.py             # Pydantic response models
│   └── services/
│       ├── classifier.py     # Exposure classification logic
│       ├── enhancer.py       # Enhancement functions (gamma, CLAHE, etc.)
│       └── histogram.py      # Histogram extraction & LAB channel utils
├── test_images/              # Sample images for testing
├── outputs/                  # Auto-generated enhanced image outputs
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.0 | API framework |
| Uvicorn | 0.30.6 | ASGI server |
| OpenCV (headless) | 4.10.0.84 | Histogram analysis & image processing |
| NumPy | 1.26.4 | Array operations |
| python-multipart | 0.0.9 | File upload support |

---

## v2 Roadmap

- [ ] PostgreSQL logging of enhancement history
- [ ] Batch endpoint for multiple images in one request
- [ ] Cloudinary integration for cloud image storage
- [ ] Deploy to Render
- [ ] API key authentication
- [ ] Evaluation metrics (SSIM, PSNR)
- [ ] Streamlit demo UI