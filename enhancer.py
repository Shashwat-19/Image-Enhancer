"""
Image Enhancer Pro — Image Processing Engine
Uses Pillow, OpenCV (cv2), and NumPy for comprehensive image enhancement.
"""

import io
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter


def pil_to_cv2(pil_img):
    """Convert PIL Image (RGB) to OpenCV BGR numpy array."""
    rgb = np.array(pil_img)
    if len(rgb.shape) == 2:
        return cv2.cvtColor(rgb, cv2.COLOR_GRAY2BGR)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_img):
    """Convert OpenCV BGR numpy array to PIL Image (RGB)."""
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


# ---------------------------------------------------------------------------
# Pillow-based adjustments
# ---------------------------------------------------------------------------

def adjust_brightness(img, value):
    """Brightness: value in [-100, 100], 0 = no change."""
    if value == 0:
        return img
    factor = 1.0 + value / 100.0
    return ImageEnhance.Brightness(img).enhance(factor)


def adjust_contrast(img, value):
    """Contrast: value in [-100, 100], 0 = no change."""
    if value == 0:
        return img
    factor = 1.0 + value / 100.0
    return ImageEnhance.Contrast(img).enhance(factor)


def adjust_saturation(img, value):
    """Saturation: value in [-100, 100], 0 = no change."""
    if value == 0:
        return img
    factor = 1.0 + value / 100.0
    return ImageEnhance.Color(img).enhance(factor)


def adjust_sharpness(img, value):
    """Sharpness: value in [0, 100], 0 = no change."""
    if value == 0:
        return img
    factor = 1.0 + value / 50.0  # range → 1.0 to 3.0
    return ImageEnhance.Sharpness(img).enhance(factor)


# ---------------------------------------------------------------------------
# OpenCV-based adjustments
# ---------------------------------------------------------------------------

def apply_unsharp_mask(img, value):
    """Detail / Unsharp mask: value in [0, 100], 0 = no change."""
    if value == 0:
        return img
    cv_img = pil_to_cv2(img)
    sigma = 1.0 + value / 20.0
    amount = value / 50.0
    blurred = cv2.GaussianBlur(cv_img, (0, 0), sigma)
    sharpened = cv2.addWeighted(cv_img, 1.0 + amount, blurred, -amount, 0)
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    return cv2_to_pil(sharpened)


def apply_noise_reduction(img, value):
    """Noise reduction via fastNlMeansDenoisingColored: value in [0, 100]."""
    if value == 0:
        return img
    cv_img = pil_to_cv2(img)
    h = max(1, int(value / 10.0))
    # Use a smaller search window for speed
    denoised = cv2.fastNlMeansDenoisingColored(cv_img, None, h, h, 7, 21)
    return cv2_to_pil(denoised)


# ---------------------------------------------------------------------------
# NumPy-based adjustments
# ---------------------------------------------------------------------------

def adjust_warmth(img, value):
    """Warmth / Coolness: value in [-100, 100]. Positive = warm, negative = cool."""
    if value == 0:
        return img
    arr = np.array(img, dtype=np.float32)
    shift = value * 0.15  # subtle shift
    arr[:, :, 0] = np.clip(arr[:, :, 0] + shift, 0, 255)       # R
    arr[:, :, 2] = np.clip(arr[:, :, 2] - shift, 0, 255)       # B
    arr[:, :, 1] = np.clip(arr[:, :, 1] + shift * 0.2, 0, 255) # slight G for natural warmth
    return Image.fromarray(arr.astype(np.uint8))


def adjust_highlights(img, value):
    """Highlights: value in [-100, 100]. Affects bright regions only."""
    if value == 0:
        return img
    arr = np.array(img, dtype=np.float32)
    # Compute luminance
    luminance = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    # Mask for highlights (bright pixels)
    mask = np.clip((luminance - 128) / 127.0, 0, 1)
    mask = mask[:, :, np.newaxis]
    adjustment = value * 0.8
    arr = arr + adjustment * mask
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def adjust_shadows(img, value):
    """Shadows: value in [-100, 100]. Affects dark regions only."""
    if value == 0:
        return img
    arr = np.array(img, dtype=np.float32)
    luminance = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    # Mask for shadows (dark pixels)
    mask = np.clip((128 - luminance) / 128.0, 0, 1)
    mask = mask[:, :, np.newaxis]
    adjustment = value * 0.8
    arr = arr + adjustment * mask
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def apply_vignette(img, value):
    """Vignette: value in [0, 100]. Darkens edges progressively."""
    if value == 0:
        return img
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    # Create radial gradient
    cx, cy = w / 2, h / 2
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    # Normalize distance and compute vignette mask
    norm_dist = dist / max_dist
    strength = value / 100.0
    vignette_mask = 1.0 - strength * (norm_dist ** 2)
    vignette_mask = np.clip(vignette_mask, 0, 1)[:, :, np.newaxis]
    arr = arr * vignette_mask
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


# ---------------------------------------------------------------------------
# Transform helpers (rotate / flip)
# ---------------------------------------------------------------------------

def apply_transforms(img, transforms):
    """Apply rotation and flip transforms."""
    rotation = transforms.get('rotation', 0)
    flip_h = transforms.get('flipH', False)
    flip_v = transforms.get('flipV', False)

    if rotation == 90:
        img = img.transpose(Image.ROTATE_270)
    elif rotation == 180:
        img = img.transpose(Image.ROTATE_180)
    elif rotation == 270:
        img = img.transpose(Image.ROTATE_90)

    if flip_h:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    return img


# ---------------------------------------------------------------------------
# Main enhancement pipeline
# ---------------------------------------------------------------------------

def enhance_image(img, params):
    """
    Apply all enhancements in order.
    params keys: brightness, contrast, saturation, warmth, highlights, shadows,
                 sharpness, detail, noiseReduction, vignette, transforms
    """
    img = img.convert('RGB')

    # Apply transforms first
    transforms = params.get('transforms', {})
    if transforms:
        img = apply_transforms(img, transforms)

    # Light & Tone
    img = adjust_brightness(img, params.get('brightness', 0))
    img = adjust_contrast(img, params.get('contrast', 0))
    img = adjust_highlights(img, params.get('highlights', 0))
    img = adjust_shadows(img, params.get('shadows', 0))

    # Color
    img = adjust_saturation(img, params.get('saturation', 0))
    img = adjust_warmth(img, params.get('warmth', 0))

    # Detail & Texture
    img = adjust_sharpness(img, params.get('sharpness', 0))
    img = apply_unsharp_mask(img, params.get('detail', 0))
    img = apply_noise_reduction(img, params.get('noiseReduction', 0))

    # Effects
    img = apply_vignette(img, params.get('vignette', 0))

    return img


# ---------------------------------------------------------------------------
# Auto-enhance analysis & correction
# ---------------------------------------------------------------------------

def auto_analyze(img):
    """
    Analyze image properties:
    - Mean brightness (0-255)
    - Contrast proxy (std dev of luminance)
    - Color cast detection (warm / cool / neutral)
    """
    img = img.convert('RGB')
    arr = np.array(img, dtype=np.float32)

    # Luminance
    luminance = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    mean_brightness = float(np.mean(luminance))
    contrast_std = float(np.std(luminance))

    # Channel means for cast detection
    r_mean = float(np.mean(arr[:, :, 0]))
    g_mean = float(np.mean(arr[:, :, 1]))
    b_mean = float(np.mean(arr[:, :, 2]))

    overall_mean = (r_mean + g_mean + b_mean) / 3.0
    r_dev = r_mean - overall_mean
    b_dev = b_mean - overall_mean

    if r_dev > 5:
        tone = 'warm'
    elif b_dev > 5:
        tone = 'cool'
    else:
        tone = 'neutral'

    return {
        'brightness': round(mean_brightness, 1),
        'contrast': round(contrast_std, 1),
        'tone': tone,
        'r_mean': round(r_mean, 1),
        'g_mean': round(g_mean, 1),
        'b_mean': round(b_mean, 1),
    }


def compute_auto_params(analysis):
    """Compute correction parameters based on analysis."""
    params = {
        'brightness': 0,
        'contrast': 0,
        'saturation': 0,
        'warmth': 0,
        'highlights': 0,
        'shadows': 0,
        'sharpness': 0,
        'detail': 0,
        'noiseReduction': 0,
        'vignette': 0,
    }

    # Brightness correction: target ~128
    brightness = analysis['brightness']
    if brightness < 90:
        params['brightness'] = min(40, int((128 - brightness) * 0.5))
        params['shadows'] = min(30, int((128 - brightness) * 0.3))
    elif brightness > 170:
        params['brightness'] = max(-40, int((128 - brightness) * 0.4))
        params['highlights'] = max(-30, int((128 - brightness) * 0.3))

    # Contrast correction: target std ~55
    contrast = analysis['contrast']
    if contrast < 35:
        params['contrast'] = min(35, int((55 - contrast) * 0.6))
    elif contrast > 80:
        params['contrast'] = max(-25, int((55 - contrast) * 0.3))

    # Color cast correction
    tone = analysis['tone']
    if tone == 'warm':
        params['warmth'] = -15
    elif tone == 'cool':
        params['warmth'] = 15

    # Add a bit of sharpness and saturation boost
    params['sharpness'] = 15
    params['saturation'] = 10
    params['detail'] = 10

    return params


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

PRESETS = {
    'Vivid': {
        'brightness': 5, 'contrast': 20, 'saturation': 35, 'warmth': 5,
        'highlights': 0, 'shadows': 10, 'sharpness': 20, 'detail': 15,
        'noiseReduction': 0, 'vignette': 0,
    },
    'Portrait': {
        'brightness': 10, 'contrast': 10, 'saturation': 5, 'warmth': 10,
        'highlights': -10, 'shadows': 15, 'sharpness': 15, 'detail': 10,
        'noiseReduction': 15, 'vignette': 20,
    },
    'Night Fix': {
        'brightness': 30, 'contrast': 15, 'saturation': 10, 'warmth': 0,
        'highlights': -5, 'shadows': 35, 'sharpness': 10, 'detail': 20,
        'noiseReduction': 40, 'vignette': 0,
    },
    'Cinematic': {
        'brightness': -5, 'contrast': 25, 'saturation': -10, 'warmth': -10,
        'highlights': -15, 'shadows': -10, 'sharpness': 10, 'detail': 5,
        'noiseReduction': 0, 'vignette': 35,
    },
    'B&W': {
        'brightness': 5, 'contrast': 30, 'saturation': -100, 'warmth': 0,
        'highlights': 10, 'shadows': -10, 'sharpness': 20, 'detail': 10,
        'noiseReduction': 0, 'vignette': 15,
    },
    'Warm': {
        'brightness': 5, 'contrast': 5, 'saturation': 15, 'warmth': 35,
        'highlights': 5, 'shadows': 10, 'sharpness': 10, 'detail': 0,
        'noiseReduction': 0, 'vignette': 10,
    },
    'Cool': {
        'brightness': 0, 'contrast': 10, 'saturation': 10, 'warmth': -30,
        'highlights': 5, 'shadows': 5, 'sharpness': 15, 'detail': 5,
        'noiseReduction': 0, 'vignette': 5,
    },
    'Airy': {
        'brightness': 20, 'contrast': -10, 'saturation': -5, 'warmth': 5,
        'highlights': 15, 'shadows': 20, 'sharpness': 5, 'detail': 0,
        'noiseReduction': 10, 'vignette': 0,
    },
    'Moody': {
        'brightness': -15, 'contrast': 20, 'saturation': -15, 'warmth': -5,
        'highlights': -20, 'shadows': -15, 'sharpness': 10, 'detail': 5,
        'noiseReduction': 5, 'vignette': 40,
    },
}
