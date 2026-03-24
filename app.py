"""
Image Enhancer Pro — Flask Application
REST API for image enhancement with Pillow, OpenCV, and NumPy.
"""

import io
import base64
import json
from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image

from enhancer import enhance_image, auto_analyze, compute_auto_params, PRESETS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


def decode_base64_image(b64_string):
    """Decode a base64 string (with or without data URI prefix) to a PIL Image."""
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]
    img_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(img_data))


def encode_image_to_base64(img, fmt='PNG', quality=95):
    """Encode a PIL Image to a base64 data URI string."""
    buf = io.BytesIO()
    save_kwargs = {}
    if fmt.upper() == 'JPEG':
        img = img.convert('RGB')
        save_kwargs['quality'] = quality
    elif fmt.upper() == 'WEBP':
        save_kwargs['quality'] = quality
    img.save(buf, format=fmt.upper(), **save_kwargs)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    mime = {
        'PNG': 'image/png',
        'JPEG': 'image/jpeg',
        'WEBP': 'image/webp',
        'BMP': 'image/bmp',
        'TIFF': 'image/tiff',
    }.get(fmt.upper(), 'image/png')
    return f'data:{mime};base64,{b64}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/enhance', methods=['POST'])
def enhance():
    """
    Accept JSON: { image: base64_string, params: { brightness, contrast, ... } }
    Return JSON: { image: base64_enhanced }
    """
    try:
        data = request.get_json(force=True)
        b64_image = data.get('image', '')
        params = data.get('params', {})

        if not b64_image:
            return jsonify({'error': 'No image provided'}), 400

        img = decode_base64_image(b64_image)
        enhanced = enhance_image(img, params)
        result_b64 = encode_image_to_base64(enhanced, 'PNG')

        return jsonify({'image': result_b64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def download():
    """
    Accept JSON: { image: base64_string, params: {...}, format: 'PNG'|'JPEG'|'WEBP', quality: 95 }
    Return processed image as file download.
    """
    try:
        data = request.get_json(force=True)
        b64_image = data.get('image', '')
        params = data.get('params', {})
        fmt = data.get('format', 'PNG').upper()
        quality = int(data.get('quality', 95))

        if fmt not in ('PNG', 'JPEG', 'WEBP'):
            fmt = 'PNG'

        if not b64_image:
            return jsonify({'error': 'No image provided'}), 400

        img = decode_base64_image(b64_image)
        enhanced = enhance_image(img, params)

        buf = io.BytesIO()
        save_kwargs = {}
        if fmt == 'JPEG':
            enhanced = enhanced.convert('RGB')
            save_kwargs['quality'] = quality
        elif fmt == 'WEBP':
            save_kwargs['quality'] = quality

        enhanced.save(buf, format=fmt, **save_kwargs)
        buf.seek(0)

        ext = fmt.lower()
        if ext == 'jpeg':
            ext = 'jpg'

        mime = {
            'PNG': 'image/png',
            'JPEG': 'image/jpeg',
            'WEBP': 'image/webp',
        }.get(fmt, 'image/png')

        return send_file(
            buf,
            mimetype=mime,
            as_attachment=True,
            download_name=f'enhanced.{ext}'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auto_enhance', methods=['POST'])
def auto_enhance():
    """
    Accept JSON: { image: base64_string }
    Analyze image, compute corrections, apply, and return enhanced image + analysis + params.
    """
    try:
        data = request.get_json(force=True)
        b64_image = data.get('image', '')

        if not b64_image:
            return jsonify({'error': 'No image provided'}), 400

        img = decode_base64_image(b64_image)
        analysis = auto_analyze(img)
        params = compute_auto_params(analysis)
        enhanced = enhance_image(img, params)
        result_b64 = encode_image_to_base64(enhanced, 'PNG')

        return jsonify({
            'image': result_b64,
            'analysis': analysis,
            'params': params,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/presets', methods=['GET'])
def presets():
    """Return all preset configurations."""
    return jsonify(PRESETS)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
