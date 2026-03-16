# Histogram Image Enhancer Experiment Report

## 1. Aim of the Experiment
**Automated Exposure Control: An Applied Exploration of Histogram Analysis, LAB Color Space, and Programmatic Image Enhancement for Student Innovators**

## 2. Equipment Required
- **Programming Language**: Python 3.x
- **Core Libraries**:
  - `opencv-python-headless` (4.10.0.84) for image processing and histogram analysis.
  - `numpy` (1.26.4) for efficient array operations and statistical calculations.
- **Web Frameworks**:
  - `fastapi` (0.115.0) and `uvicorn` (0.30.6) for the RESTful backend API server.
  - `streamlit` (1.55.0) for the interactive web frontend frontend.
- **Other Dependencies**: `python-multipart` (for handling file uploads), `requests` (for inter-service API communication), `Pillow` (for image loading), and `matplotlib` (for generating histogram visualizations).
- **Environment**: Python Virtual environment (`venv`), Git.

## 3. Theory
The core concept driving this system is the isolation of image *lightness* from color information to determine the necessary enhancement without causing color distortion or unwanted hues.

**Color Spaces**: 
Standard images use the BGR (Blue, Green, Red) or RGB color space, where intensity and color are entangled. This project converts the image into the **LAB color space**, which separates Lightness (the L channel) from color components (A and B channels). All statistical analysis and intensity modifications are performed strictly on the L channel.

**Histogram Analysis**: 
The L channel represents pixel intensities on a scale from 0 (pure black) to 255 (pure white). By computing the statistical **mean** (average pixel intensity) and **standard deviation** (the spread of intensities, representing contrast), the system classifies the exposure condition:
- *Underexposed*: Mean < 80 (The image is overall too dark).
- *Overexposed*: Mean > 180 (The image is overall too bright).
- *Low Contrast*: Standard Deviation < 40 (The pixel distribution is narrow, lacking depth).
- *Normal*: Falls comfortably within normal thresholds.

**Enhancement Algorithms**:
- **Gamma Correction**: Modifies pixel intensities non-linearly using a power-law relationship ($V_{out} = V_{in}^\gamma$). A fractional gamma ($\gamma = 0.4$) stretches the lower intensities, effectively recovering details in shadowed regions for underexposed images.
- **Tone Compression**: The same power-law function is applied but with $\gamma > 1$ (e.g., $\gamma = 1.8$). This compresses higher intensities, reducing brightness to restore mid-tones for overexposed images.
- **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Standard histogram equalization often over-amplifies noise in flat areas. CLAHE mitigates this by dividing the image into small tiles (e.g., $8 \times 8$) and equalizing them individually, while explicitly clipping the histogram distribution at a specific limit to prevent excessive, artificial-looking contrast enhancements.

## 4. GitHub Link
[GitHub Repository Link - Insert Here]
Branch: `main` 

## 5. Procedure
Follow these steps to replicate the experiment and run the project locally.

**Step 1: Clone the Repository**
Open a terminal and download the project via Git:
```bash
git clone https://github.com/YOUR_USERNAME/histogram-enhancer.git
cd histogram-enhancer
```

**Step 2: Environment Setup**
Create and activate a Python virtual environment to securely isolate project dependencies:
```bash
python -m venv venv

# On macOS and Linux:
source venv/bin/activate  

# On Windows:
# venv\Scripts\activate
```

**Step 3: Install Dependencies**
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

**Step 4: Launch the API Server**
Start the FastAPI backend with live-reloading enabled:
```bash
uvicorn app.main:app --reload
```
The API documentation (Swagger UI) is automatically generated and available at `http://localhost:8000/docs`.

**Step 5: Run the Web Interface**
Open a new terminal window, activate the virtual environment again, and launch the Streamlit app:
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```
The application interface will open in the default web browser at `http://localhost:8501`.

## 6. Code Explanation
The application logic is modularized into an API layer and specialized processing services.

- **`app/main.py` (API Layer)**: This file contains the main FastAPI application and HTTP route definitions. The `/enhance` endpoint is the system's entry point. It accepts incoming image uploads, validates them (JPEG/PNG, max size 10MB), and orchestrates the processing pipeline. It coordinates the services by calling the functions to extract the L channel, classify the exposure condition, apply the mapped enhancement, merge the channels back, save the output to the `outputs` directory, and finally format the HTTP response returning the new image with custom headers detailing the metrics.

- **`app/services/histogram.py` (Analysis Utilities)**: Contains helper functions for image conversion and statistical extraction. The `get_lightness_channel()` function leverages `cv2.cvtColor` to convert the image from BGR to LAB and explicitly extracts the first channel (L). The `compute_stats()` function calculates the mean and standard deviation of this array, providing the raw data points needed for the decision logic.

- **`app/services/classifier.py` (Decision Logic)**: This module defines `ExposureCondition` through an Enum. The `classify(mean, std)` function acts as the deterministic brain of the system. Using predefined numerical thresholds tailored for 0-255 scaling, it determines whether the provided stats indicate `UNDEREXPOSED`, `OVEREXPOSED`, `LOW_CONTRAST`, or `NORMAL`. It pairs these conditions to their corresponding enhancement method string names using the `METHOD_MAP` dictionary.

- **`app/services/enhancer.py` (Enhancement Implementations)**: Contains the core mathematical corrections acting strictly on the provided L channel array. It includes functions like `gamma_correct()` which scales intensities relative to $\gamma = 0.4$, `tone_compress()` relative to $\gamma = 1.8$, and `clahe_enhance()` which uses `cv2.createCLAHE`. A strategy map (`ENHANCE_FUNCTIONS`) links the string methods mapped in the classifier directly to these callable functions, ensuring an extensible design.

## 7. Observations

**Scenario 1: Testing an Underexposed Image**
- **Test Objective**: Verify if a visually dark image predictably triggers the underexposed classifier and brightens appropriately without color washout.
- **Observed Behavior**: The system successfully measured an L channel mean below 80 and correctly classified the condition as `UNDEREXPOSED`. The mapped `gamma_correction` method was applied. The output image successfully amplified shadowed pixel intensities, revealing background details while protecting the original color hues.
[Image: Screenshot of output for Case 1 (Underexposed)]

**Scenario 2: Testing an Overexposed Image**
- **Test Objective**: Verify if an overly bright image triggers tone compression correctly.
- **Observed Behavior**: The extracted mean was above 180, leading to an accurate `OVEREXPOSED` classification. The applied `tone_compression` algorithm ($\gamma = 1.8$) selectively darkened blown-out highlights, restoring mid-tones and noticeably improving the visibility of washed-out textures.
[Image: Screenshot of output for Case 2 (Overexposed)]

**Scenario 3: Testing a Low-Contrast Image**
- **Test Objective**: Evaluate behavior on an image exhibiting flat, gray lighting but normal overall brightness.
- **Observed Behavior**: While the mean was normal, the standard deviation of the L channel dipped below the threshold of 40, resulting in a `LOW_CONTRAST` classification. The system correctly passed the array to `CLAHE`, which enhanced local contrast significantly. Edges were rendered sharper and structural outlines more distinct without the noise magnification commonly associated with global histogram equalization.
[Image: Screenshot of output for Case 3 (Low Contrast)]

**Scenario 4: Testing a Normally Exposed Image**
- **Test Objective**: Ensure the system's condition thresholds prevent it from unnecessarily distorting an already balanced image.
- **Observed Behavior**: Both the mean and standard deviation fell within normal, un-flagged ranges. The system classified the image as `NORMAL` and appropriately executed the `passthrough` technique, simply returning the unmodified L channel. The resulting output was identical to the input, demonstrating the pipeline's required non-destructive capability.
[Image: Screenshot of output for Case 4 (Normal)]

## 8. Conclusion
This experiment successfully validated the use of statistical histogram analysis within the LAB color space for the automated detection and correction of image exposure issues. By isolating the lightness channel (L) before modifying pixel intensities, we effectively adjusted brightness and contrast computationally without introducing detrimental color shifts.

**Key Learnings**:
Separating the threshold-based decision logic (in the classifier service) from the actual enhancement algorithms proved highly effective from an engineering standpoint. Furthermore, we confirmed that established techniques like Gamma Correction and CLAHE remain powerful, straightforward solutions, providing rapid and deterministic enhancements suitable for synchronous, real-time web applications. Specifically, CLAHE visibly outperformed global histogram equalization by retaining natural textures in low-contrast image testing.

**Limitations**:
A measurable limitation is the system's reliance on hardcoded, fixed thresholds (e.g., mean < 80 for underexposure). While demonstrably effective for standardized photos, these firm boundaries are susceptible to misclassifying images that exhibit intentionally unbalanced lighting by artistic design—such as low-key photography, silhouettes, or night scenes. 

**Future Improvements**:
Future iterations of this software could introduce adaptive, intelligent thresholding leveraging image entropy, or by integrating lightweight Deep Learning classifiers for more scene-aware exposure detection. Additionally, adopting a sliding, continuous scale to dynamically compute the exact $\gamma$ parameter based on the precise severity of the measured mean deviation—rather than relying on fixed constants (0.4 and 1.8)—would yield smoother, more natural corrections for borderline exposures.
