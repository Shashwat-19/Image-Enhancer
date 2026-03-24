/* ============================================================
   Image Enhancer Pro — Frontend Application Logic
   ============================================================ */

(function () {
    'use strict';

    // ── State ──────────────────────────────────────────────
    const state = {
        originalBase64: null,
        viewMode: 'split', // 'split' | 'before' | 'after'
        transforms: { rotation: 0, flipH: false, flipV: false },
        activePreset: null,
        processing: false,
        params: {
            brightness: 0, contrast: 0, highlights: 0, shadows: 0,
            sharpness: 0, detail: 0, noiseReduction: 0,
            saturation: 0, warmth: 0, vignette: 0,
        },
    };

    const DEFAULTS = { ...state.params };

    // ── DOM Refs ───────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const uploadZone    = $('#upload-zone');
    const uploadInput   = $('#upload-input');
    const canvasArea    = $('#canvas-area');
    const panelOriginal = $('#panel-original');
    const panelEnhanced = $('#panel-enhanced');
    const imgOriginal   = $('#img-original');
    const imgEnhanced   = $('#img-enhanced');
    const loadingOverlay = $('#loading-overlay');
    const sidebar       = $('#sidebar');
    const autoStats     = $('#auto-stats');
    const toastContainer = $('#toast-container');

    // ── Debounce helper ────────────────────────────────────
    function debounce(fn, ms) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), ms);
        };
    }

    // ── Toast Notifications ────────────────────────────────
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icon = type === 'success' ? '✓' : '✕';
        toast.innerHTML = `<span class="toast-icon">${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);
        requestAnimationFrame(() => {
            requestAnimationFrame(() => toast.classList.add('show'));
        });
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ── Upload Handling ────────────────────────────────────
    uploadZone.addEventListener('click', () => uploadInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });

    uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });

    function handleFile(file) {
        const validTypes = ['image/png', 'image/jpeg', 'image/webp', 'image/bmp', 'image/tiff'];
        if (!validTypes.includes(file.type)) {
            showToast('Unsupported format. Use PNG, JPEG, WEBP, BMP, or TIFF.', 'error');
            return;
        }
        if (file.size > 16 * 1024 * 1024) {
            showToast('File too large. Maximum 16 MB.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            state.originalBase64 = e.target.result;
            imgOriginal.src = state.originalBase64;
            imgEnhanced.src = state.originalBase64;
            uploadZone.classList.add('hidden');
            sidebar.classList.remove('disabled');
            resetAllParams();
            showToast('Image loaded successfully');
        };
        reader.readAsDataURL(file);
    }

    // New Image button
    $('#btn-new-image').addEventListener('click', () => {
        state.originalBase64 = null;
        imgOriginal.src = '';
        imgEnhanced.src = '';
        uploadZone.classList.remove('hidden');
        sidebar.classList.add('disabled');
        autoStats.classList.remove('visible');
        resetAllParams();
        uploadInput.value = '';
    });

    // ── Slider Setup ───────────────────────────────────────
    const sliders = {};
    const debouncedEnhance = debounce(() => callEnhanceAPI(), 300);

    $$('.slider-track').forEach((slider) => {
        const param = slider.dataset.param;
        const valueDisplay = slider.closest('.slider-control').querySelector('.slider-value');
        sliders[param] = { el: slider, display: valueDisplay };

        slider.addEventListener('input', () => {
            const val = parseInt(slider.value, 10);
            state.params[param] = val;
            valueDisplay.textContent = val > 0 ? `+${val}` : val;
            state.activePreset = null;
            $$('.preset-btn').forEach(b => b.classList.remove('active'));
            debouncedEnhance();
        });
    });

    function setSliderValues(params) {
        for (const [key, val] of Object.entries(params)) {
            if (sliders[key]) {
                sliders[key].el.value = val;
                sliders[key].display.textContent = val > 0 ? `+${val}` : val;
                state.params[key] = val;
            }
        }
    }

    function resetAllParams() {
        setSliderValues(DEFAULTS);
        state.transforms = { rotation: 0, flipH: false, flipV: false };
        state.activePreset = null;
        $$('.preset-btn').forEach(b => b.classList.remove('active'));
        autoStats.classList.remove('visible');
    }

    // ── Presets ────────────────────────────────────────────
    let presetsData = {};

    async function loadPresets() {
        try {
            const resp = await fetch('/presets');
            presetsData = await resp.json();
        } catch (e) {
            console.error('Failed to load presets:', e);
        }
    }

    $$('.preset-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const name = btn.dataset.preset;
            const preset = presetsData[name];
            if (!preset || !state.originalBase64) return;

            $$('.preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.activePreset = name;

            setSliderValues(preset);
            callEnhanceAPI();
        });
    });

    // ── View Mode ──────────────────────────────────────────
    function updateViewMode() {
        const mode = state.viewMode;
        panelOriginal.style.display = mode === 'after' ? 'none' : 'flex';
        panelEnhanced.style.display = mode === 'before' ? 'none' : 'flex';

        $$('.view-btn').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.view === mode);
        });
    }

    $$('.view-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            state.viewMode = btn.dataset.view;
            updateViewMode();
        });
    });

    // ── Rotate / Flip ──────────────────────────────────────
    $('#btn-rotate-l').addEventListener('click', () => {
        state.transforms.rotation = (state.transforms.rotation + 270) % 360;
        if (state.originalBase64) callEnhanceAPI();
    });

    $('#btn-rotate-r').addEventListener('click', () => {
        state.transforms.rotation = (state.transforms.rotation + 90) % 360;
        if (state.originalBase64) callEnhanceAPI();
    });

    $('#btn-flip-h').addEventListener('click', () => {
        state.transforms.flipH = !state.transforms.flipH;
        if (state.originalBase64) callEnhanceAPI();
    });

    $('#btn-flip-v').addEventListener('click', () => {
        state.transforms.flipV = !state.transforms.flipV;
        if (state.originalBase64) callEnhanceAPI();
    });

    // ── API: Enhance ───────────────────────────────────────
    async function callEnhanceAPI() {
        if (!state.originalBase64 || state.processing) return;
        state.processing = true;
        loadingOverlay.classList.add('active');

        try {
            const resp = await fetch('/enhance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: state.originalBase64,
                    params: { ...state.params, transforms: state.transforms },
                }),
            });

            if (!resp.ok) throw new Error('Enhancement failed');
            const data = await resp.json();
            if (data.error) throw new Error(data.error);

            imgEnhanced.src = data.image;
        } catch (e) {
            showToast(e.message || 'Enhancement failed', 'error');
        } finally {
            state.processing = false;
            loadingOverlay.classList.remove('active');
        }
    }

    // ── API: Auto Enhance ──────────────────────────────────
    $('#btn-auto-enhance').addEventListener('click', async () => {
        if (!state.originalBase64 || state.processing) return;
        state.processing = true;
        loadingOverlay.classList.add('active');

        try {
            const resp = await fetch('/auto_enhance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: state.originalBase64 }),
            });

            if (!resp.ok) throw new Error('Auto enhance failed');
            const data = await resp.json();
            if (data.error) throw new Error(data.error);

            // Update sliders with auto params
            setSliderValues(data.params);
            state.transforms = { rotation: 0, flipH: false, flipV: false };

            // Update enhanced image
            imgEnhanced.src = data.image;

            // Show analysis stats
            const a = data.analysis;
            $('#stat-brightness').textContent = `${Math.round(a.brightness)} / 255`;
            $('#stat-contrast').textContent = `${Math.round(a.contrast)}`;

            const toneEl = $('#stat-tone');
            toneEl.textContent = a.tone.charAt(0).toUpperCase() + a.tone.slice(1);
            toneEl.className = `stat-value tone-${a.tone}`;

            autoStats.classList.add('visible');
            showToast('Auto enhancement applied');
        } catch (e) {
            showToast(e.message || 'Auto enhance failed', 'error');
        } finally {
            state.processing = false;
            loadingOverlay.classList.remove('active');
        }
    });

    // ── Reset ──────────────────────────────────────────────
    $('#btn-reset').addEventListener('click', () => {
        if (!state.originalBase64) return;
        resetAllParams();
        imgEnhanced.src = state.originalBase64;
        showToast('All settings reset');
    });

    // ── Download ───────────────────────────────────────────
    $('#btn-download').addEventListener('click', async () => {
        if (!state.originalBase64 || state.processing) return;
        state.processing = true;
        loadingOverlay.classList.add('active');

        const fmt = $('#export-format').value;
        const quality = parseInt($('#export-quality').value, 10) || 95;

        try {
            const resp = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: state.originalBase64,
                    params: { ...state.params, transforms: state.transforms },
                    format: fmt,
                    quality: quality,
                }),
            });

            if (!resp.ok) throw new Error('Download failed');

            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `enhanced.${fmt.toLowerCase() === 'jpeg' ? 'jpg' : fmt.toLowerCase()}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('Download started');
        } catch (e) {
            showToast(e.message || 'Download failed', 'error');
        } finally {
            state.processing = false;
            loadingOverlay.classList.remove('active');
        }
    });

    // ── Init ───────────────────────────────────────────────
    sidebar.classList.add('disabled');
    updateViewMode();
    loadPresets();

})();
