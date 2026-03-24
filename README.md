<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Pillow-10.x-3776AB?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-1.24+-013243?style=for-the-badge&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-6ee7b7?style=for-the-badge" />
</p>

<h1 align="center">✦ Image Enhancer Pro</h1>

<p align="center">
  <strong>A professional-grade image enhancement web application built with Flask, Pillow, OpenCV, and NumPy.</strong><br/>
  Think Lightroom meets Linear — a premium, dark-themed photo editor in your browser.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#presets">Presets</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## Features

### 🎛️ Comprehensive Enhancement Controls

| Category | Controls | Engine |
|---|---|---|
| **Light & Tone** | Brightness, Contrast, Highlights, Shadows | Pillow + NumPy |
| **Detail & Texture** | Sharpness, Detail (Unsharp Mask), Noise Reduction | Pillow + OpenCV |
| **Color** | Saturation, Warmth / Coolness | Pillow + NumPy |
| **Effects** | Vignette (Radial Gradient Overlay) | NumPy |
| **Transform** | Rotate Left/Right, Flip Horizontal/Vertical | Pillow |

### ✦ Auto Enhance
AI-powered image analysis that measures:
- **Mean brightness** (luminance average)
- **Contrast proxy** (standard deviation of luminance)
- **Color cast detection** (RGB channel dominance → warm / cool / neutral)

Automatically applies optimal corrections based on the analysis.

### 🎨 9 Curated Presets
One-click professional looks:
**Vivid** · **Portrait** · **Night Fix** · **Cinematic** · **B&W** · **Warm** · **Cool** · **Airy** · **Moody**

### 🖥️ Premium Dark UI
- **Dark theme** — deep charcoal (`#0b0c0f`) with layered surfaces
- **Typography** — Syne for headings, DM Mono for values and labels
- **Accent palette** — mint green (`#6ee7b7`) primary, blue (`#3b82f6`) secondary
- **Split view** — side-by-side Original | Enhanced with toggle modes
- **Micro-animations** — smooth 0.15–0.25s transitions on every interaction
- **Drag & drop** upload with animated hover state
- **Live preview** — 300ms debounced slider updates
- **Toast notifications** for success/error feedback

### 📦 Export
Download enhanced images in **PNG**, **JPEG**, or **WEBP** with adjustable quality.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Flask | REST API server |
| **Image Processing** | Pillow (PIL) | Brightness, contrast, saturation, sharpness |
| **Advanced Processing** | OpenCV (cv2) | Unsharp mask, noise reduction |
| **Pixel Operations** | NumPy | Warmth, highlights/shadows, vignette |
| **Frontend** | Vanilla JS + CSS | Zero-dependency, premium dark UI |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Shashwat-19/Image-Enhancer.git
cd Image-Enhancer

# Install dependencies
pip install -r requirements.txt

# Start the server
python3 app.py
```

Open **http://127.0.0.1:8080** in your browser.

### Usage

1. **Upload** — Drag & drop an image or click to browse (PNG, JPEG, WEBP, BMP, TIFF up to 16 MB)
2. **Adjust** — Use sliders for fine-tuned control or click a preset for instant styling
3. **Auto Enhance** — Let the engine analyze and correct your image automatically
4. **Export** — Choose format and quality, then download

---

## Project Structure

```
image_enhancer/
├── app.py               # Flask application & REST API routes
├── enhancer.py          # Image processing engine
├── requirements.txt     # Python dependencies
├── .gitignore
├── templates/
│   └── index.html       # Frontend markup
└── static/
    ├── style.css        # Dark theme styles
    └── app.js           # Frontend application logic
```

---

## API Reference

### `POST /enhance`
Process an image with specified parameters.

**Request:**
```json
{
  "image": "data:image/png;base64,...",
  "params": {
    "brightness": 20,
    "contrast": 10,
    "saturation": 15,
    "warmth": 0,
    "highlights": 0,
    "shadows": 0,
    "sharpness": 25,
    "detail": 10,
    "noiseReduction": 0,
    "vignette": 0,
    "transforms": { "rotation": 0, "flipH": false, "flipV": false }
  }
}
```

**Response:**
```json
{
  "image": "data:image/png;base64,..."
}
```

---

### `POST /auto_enhance`
Analyze image properties and apply automatic corrections.

**Request:**
```json
{
  "image": "data:image/png;base64,..."
}
```

**Response:**
```json
{
  "image": "data:image/png;base64,...",
  "analysis": {
    "brightness": 127.6,
    "contrast": 42.3,
    "tone": "warm",
    "r_mean": 200.0,
    "g_mean": 100.0,
    "b_mean": 80.0
  },
  "params": {
    "brightness": 0,
    "contrast": 33,
    "warmth": -15,
    "sharpness": 15,
    "saturation": 10,
    "detail": 10
  }
}
```

---

### `POST /download`
Download the processed image as a file.

**Request:**
```json
{
  "image": "data:image/png;base64,...",
  "params": { ... },
  "format": "PNG",
  "quality": 95
}
```

**Response:** Binary file download.

---

### `GET /presets`
Returns all available preset configurations.

**Response:**
```json
{
  "Vivid": { "brightness": 5, "contrast": 20, "saturation": 35, ... },
  "Portrait": { ... },
  ...
}
```

---

## Slider Parameter Ranges

| Parameter | Min | Max | Default |
|---|---|---|---|
| Brightness | -100 | 100 | 0 |
| Contrast | -100 | 100 | 0 |
| Highlights | -100 | 100 | 0 |
| Shadows | -100 | 100 | 0 |
| Saturation | -100 | 100 | 0 |
| Warmth | -100 | 100 | 0 |
| Sharpness | 0 | 100 | 0 |
| Detail | 0 | 100 | 0 |
| Noise Reduction | 0 | 100 | 0 |
| Vignette | 0 | 100 | 0 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Upload   │  │  Sliders │  │  Presets │             │
│  │  Zone     │  │  Panel   │  │  Grid    │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │              │              │                   │
│       └──────────────┼──────────────┘                   │
│                      │ Base64 + Params (JSON)           │
└──────────────────────┼──────────────────────────────────┘
                       │ HTTP POST
┌──────────────────────┼──────────────────────────────────┐
│                Flask API (app.py)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ /enhance │  │/download │  │/auto_    │  │/presets│ │
│  │          │  │          │  │ enhance  │  │        │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┘ │
│       └──────────────┼──────────────┘                   │
│                      │                                  │
│           ┌──────────┴──────────┐                       │
│           │  enhancer.py        │                       │
│           │  ┌──────┐ ┌──────┐ │                       │
│           │  │Pillow│ │OpenCV│ │                       │
│           │  └──────┘ └──────┘ │                       │
│           │  ┌──────┐          │                       │
│           │  │NumPy │          │                       │
│           │  └──────┘          │                       │
│           └─────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

---

## Presets

| Preset | Style | Key Adjustments |
|---|---|---|
| **Vivid** | Vibrant, punchy | ↑ Saturation +35, ↑ Contrast +20 |
| **Portrait** | Soft, flattering | ↑ Warmth +10, Vignette +20, NR +15 |
| **Night Fix** | Low-light recovery | ↑ Brightness +30, ↑ Shadows +35, NR +40 |
| **Cinematic** | Film-like mood | ↑ Contrast +25, ↓ Saturation -10, Vignette +35 |
| **B&W** | Classic monochrome | Saturation -100, ↑ Contrast +30 |
| **Warm** | Golden tones | ↑ Warmth +35, ↑ Saturation +15 |
| **Cool** | Blue-tinted | ↓ Warmth -30, ↑ Contrast +10 |
| **Airy** | Light, ethereal | ↑ Brightness +20, ↓ Contrast -10 |
| **Moody** | Dark, dramatic | ↓ Brightness -15, Vignette +40, ↓ Saturation -15 |

---

## Supported Formats

| Format | Upload | Export |
|---|---|---|
| PNG | ✅ | ✅ |
| JPEG | ✅ | ✅ |
| WEBP | ✅ | ✅ |
| BMP | ✅ | — |
| TIFF | ✅ | — |

Max file size: **16 MB**

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Author

**Shashwat**
- GitHub: [@Shashwat-19](https://github.com/Shashwat-19)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using Flask, Pillow, OpenCV & NumPy
</p>