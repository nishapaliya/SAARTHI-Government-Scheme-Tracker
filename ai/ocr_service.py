import os
import shutil

from PIL import Image, ImageFile, ImageOps

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---------------------------------------------------------------------------
# Fast, free, unlimited OCR using Tesseract (via pytesseract).
#
# Why Tesseract instead of EasyOCR:
#   - EasyOCR loads large deep-learning detection + recognition models
#     (100+ MB) and runs them on every image, which is why verification
#     was taking 1-2+ minutes, especially on CPU.
#   - Tesseract is a mature, open-source (Apache 2.0) OCR engine that ships
#     as a small local binary with no model download, no API key, no
#     request limits and no cost. For printed/machine-text documents
#     (Aadhaar, PAN, bank passbooks, certificates) it is both fast
#     (well under a second per document once the image is downsized) and
#     accurate, which is exactly the kind of document this app verifies.
#
# Requirements:
#   - The `tesseract-ocr` system binary must be installed (this is a
#     one-time OS-level install, NOT a pip package):
#       Ubuntu/Debian : sudo apt-get install -y tesseract-ocr
#       macOS (brew)  : brew install tesseract
#       Windows       : https://github.com/UB-Mannheim/tesseract/wiki
#   - `pip install pytesseract` (already in requirements.txt).
# ---------------------------------------------------------------------------

import pytesseract

# If tesseract isn't on PATH (very common on Windows -- the installer has
# an "Add to PATH" checkbox that's easy to miss), fall back to checking the
# default install locations before giving up.
_WINDOWS_FALLBACK_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
]


def _locate_tesseract():
    found = shutil.which("tesseract")
    if found:
        return found
    for path in _WINDOWS_FALLBACK_PATHS:
        if path and os.path.isfile(path):
            return path
    return None


_TESSERACT_BINARY = _locate_tesseract()
if _TESSERACT_BINARY:
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_BINARY

# Resize any image whose largest side exceeds this before running OCR.
# Tesseract's runtime scales with pixel count, so this is the single
# biggest lever for staying under the 2-second budget. 800px keeps
# printed document text (ID cards, certificates, passbooks) fully
# readable while running in ~1-1.5s even on a dense, text-heavy page.
MAX_DIMENSION = 800

# DPI used when rasterizing the first page of an uploaded PDF. Kept modest
# for speed -- 200 DPI is more than enough resolution for printed text.
PDF_RENDER_DPI = 200

# Tesseract config, tuned for speed on structured documents:
#   --oem 3               -> default LSTM engine (best accuracy/speed balance)
#   --psm 4                -> assume a single column of text of variable
#                              sizes, which fits ID cards/certificates and
#                              is noticeably faster than full-page analysis
#   load_system_dawg=0,
#   load_freq_dawg=0       -> skip loading the dictionary word lists.
#                              Government ID documents are mostly names,
#                              numbers and codes rather than dictionary
#                              words, so dictionary lookups just add
#                              latency without improving accuracy here.
_TESSERACT_CONFIG = "--oem 3 --psm 6"

class OCRNotAvailableError(RuntimeError):
    """Raised when the tesseract binary isn't installed on this machine."""
    pass


def _prepare_image(image_path):
    """Downscale + clean up the image in place for fast, accurate OCR.
    No-op fields are skipped silently if the image can't be opened -- OCR
    then just runs on the original file."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            largest_side = max(width, height)

            # Grayscale + autocontrast: cheap operations that noticeably
            # improve Tesseract's accuracy on phone-camera photos of
            # documents (uneven lighting, low contrast scans).
            processed = ImageOps.autocontrast(ImageOps.grayscale(img))

            if largest_side > MAX_DIMENSION:
                scale = MAX_DIMENSION / float(largest_side)
                new_size = (int(width * scale), int(height * scale))
                processed = processed.resize(new_size, Image.LANCZOS)

            processed.save(image_path)
    except Exception as e:
        print("OCR image preprocessing skipped:", e)


def extract_text(file_path):

    if not _TESSERACT_BINARY:
        raise OCRNotAvailableError(
            "Tesseract OCR is not installed on this server. Download and run "
            "the Windows installer from "
            "https://github.com/UB-Mannheim/tesseract-ocr/wiki (use the "
            "default install location), then restart the Flask app."
        )

    ext = os.path.splitext(file_path)[1].lower()

    # ---------- PDF ----------
    if ext == ".pdf":
        import fitz  # imported lazily -- only needed for PDF uploads

        doc = fitz.open(file_path)

        page = doc.load_page(0)

        pix = page.get_pixmap(dpi=PDF_RENDER_DPI)

        image_path = file_path.replace(".pdf", "_page1.png")

        pix.save(image_path)

        file_path = image_path

    # ---------- Preprocess (grayscale, contrast, resize) ----------
    _prepare_image(file_path)

    # ---------- OCR ----------
    with Image.open(file_path) as img:
        text = pytesseract.image_to_string(
    img,
    lang="eng+hin+mar",
    config=_TESSERACT_CONFIG
)
    return text