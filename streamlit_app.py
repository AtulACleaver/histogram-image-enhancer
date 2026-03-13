import streamlit as st
import requests
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt

# --- Config ---
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Histogram Image Enhancer",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 Histogram Image Enhancer")
st.markdown("Upload an image. The API detects what's wrong and fixes it automatically.")

# --- Sidebar ---
st.sidebar.header("How it works")
st.sidebar.markdown("""
1. Upload a JPEG or PNG
2. API analyzes the L-channel histogram
3. Classifies exposure condition
4. Applies the right enhancement
5. You see before/after + stats

**Conditions detected:**
- 🌑 **Underexposed** → Gamma correction
- ☀️ **Overexposed** → Tone compression
- 🌫️ **Low contrast** → CLAHE
- ✅ **Normal** → No changes needed
""")

# --- Health check ---
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    if health.status_code == 200:
        st.sidebar.success("API is running ✓")
    else:
        st.sidebar.error("API returned non-200")
except requests.exceptions.ConnectionError:
    st.sidebar.error("API not reachable. Start the server first.")
    st.stop()

# --- Upload ---
uploaded_file = st.file_uploader(
    "Drop your image here",
    type=["jpg", "jpeg", "png"],
    help="Max 10MB. JPEG or PNG only.",
)

if uploaded_file is not None:
    # Show original
    original_image = Image.open(uploaded_file)

    with st.spinner("Analyzing and enhancing..."):
        # Hit the JSON endpoint for metadata
        uploaded_file.seek(0)
        json_response = requests.post(
            f"{API_URL}/enhance/json",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
        )

        # Hit the image endpoint for the enhanced file
        uploaded_file.seek(0)
        image_response = requests.post(
            f"{API_URL}/enhance",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
        )

    if json_response.status_code != 200:
        st.error(f"API error: {json_response.text}")
        st.stop()

    metadata = json_response.json()
    enhanced_image = Image.open(io.BytesIO(image_response.content))

    # --- Results header ---
    condition = metadata["condition"]
    method = metadata["method"]

    condition_emoji = {
        "UNDEREXPOSED": "🌑",
        "OVEREXPOSED": "☀️",
        "LOW_CONTRAST": "🌫️",
        "NORMAL": "✅",
    }

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Condition", f"{condition_emoji.get(condition, '')} {condition}")
    col2.metric("Method Applied", method.replace("_", " ").title())
    col3.metric(
        "Mean Shift",
        f"{metadata['enhanced_mean']:.1f}",
        delta=f"{metadata['enhanced_mean'] - metadata['original_mean']:.1f}",
    )

    # --- Before / After ---
    st.markdown("### Before / After")
    col_before, col_after = st.columns(2)

    with col_before:
        st.image(original_image, caption="Original", use_container_width=True)

    with col_after:
        st.image(enhanced_image, caption="Enhanced", use_container_width=True)

    # --- Histogram comparison ---
    st.markdown("### Histogram Comparison")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    original_hist = metadata["original_histogram"]
    enhanced_hist = metadata["enhanced_histogram"]

    ax1.fill_between(range(256), original_hist, alpha=0.7, color="#4a90d9")
    ax1.set_title("Original Histogram")
    ax1.set_xlabel("Pixel Intensity")
    ax1.set_ylabel("Frequency")
    ax1.set_xlim(0, 255)

    ax2.fill_between(range(256), enhanced_hist, alpha=0.7, color="#50c878")
    ax2.set_title("Enhanced Histogram")
    ax2.set_xlabel("Pixel Intensity")
    ax2.set_ylabel("Frequency")
    ax2.set_xlim(0, 255)

    plt.tight_layout()
    st.pyplot(fig)

    # --- Stats table ---
    st.markdown("### Stats")
    stats_col1, stats_col2 = st.columns(2)

    with stats_col1:
        st.markdown("**Original**")
        st.write(f"Mean: `{metadata['original_mean']:.2f}`")
        st.write(f"Std Dev: `{metadata['original_std']:.2f}`")

    with stats_col2:
        st.markdown("**Enhanced**")
        st.write(f"Mean: `{metadata['enhanced_mean']:.2f}`")
        st.write(f"Std Dev: `{metadata['enhanced_std']:.2f}`")

    # --- Download button ---
    st.markdown("---")
    buf = io.BytesIO()
    enhanced_image.save(buf, format=original_image.format or "JPEG")
    st.download_button(
        label="⬇️ Download Enhanced Image",
        data=buf.getvalue(),
        file_name=f"enhanced_{uploaded_file.name}",
        mime=uploaded_file.type,
    )

else:
    st.info("Upload an image to get started.")