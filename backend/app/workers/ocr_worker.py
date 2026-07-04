import base64
import io
import logging
import numpy as np
from PIL import Image
from ..services.job_queue import celery_app

logger = logging.getLogger(__name__)

# Lazy initialization of ML model inside the worker process only
# This prevents FastAPI web workers from loading massive 500MB models into RAM globally
_ocr_model = None

def get_ocr_engine():
    global _ocr_model
    if _ocr_model is None:
        from paddleocr import PaddleOCR
        _ocr_model = PaddleOCR(use_angle_cls=True, lang='en')
    return _ocr_model

def perform_ocr_sync(image_base64: str) -> dict:
    """
    Synchronous OCR logic extracted for use when Celery/Redis is unavailable.
    """
    try:
        # 1. Decode Image
        img_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_array = np.array(image)
        
        # 2. Run Heavy OCR
        ocr = get_ocr_engine()
        result = ocr.ocr(img_array, cls=True)
        
        # 3. Format Results
        extracted_lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_info = line[1]
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        extracted_lines.append({
                            "text": text_info[0],
                            "confidence": float(text_info[1])
                        })

        return {
            "success": True,
            "raw_results": extracted_lines
        }
    except Exception as e:
        logger.error(f"Sync OCR failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@celery_app.task(name="process_ocr_image", bind=True)
def process_ocr_image(self, image_base64: str, confidence_threshold: float = 0.85):
    """
    Background worker that unblocks FastAPI. 
    It decodes a base64 string, runs the heavy PaddleOCR model, 
    and returns semi-processed text chunks to the broker backend.
    """
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Running PaddleOCR Extracting Features...'})
        return perform_ocr_sync(image_base64)
    except Exception as e:
        logger.error(f"OCR Worker Task failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
