import logging
import io
import copy
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

# Single initialization logic
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang="en"
            )
            logger.info("PaddleOCR engine initialized successfully.")
        except ImportError:
            logger.error("PaddleOCR not installed.")
            raise Exception("PaddleOCR is not installed.")
    return _ocr_engine

class OCRService:
    def __init__(self):
        self.engine = get_ocr_engine()

    def preprocess_image(self, img_bytes: bytes) -> np.ndarray:
        """
        Enhance image before OCR (grayscale, contrast, sharpen)
        """
        try:
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            # Simple preprocessing pipeline
            # 1. Grayscale
            gray = image.convert("L")
            # 2. Contrast enhancement
            enhancer = ImageEnhance.Contrast(gray)
            high_cont = enhancer.enhance(2.0)
            # 3. Sharpening
            sharp = high_cont.filter(ImageFilter.SHARPEN)
            
            # Convert back to RGB array for paddleocr
            img_array = np.array(sharp.convert("RGB"))
            return img_array
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Fallback to pure array
            return np.array(Image.open(io.BytesIO(img_bytes)).convert("RGB"))

    def extract_text_with_confidence(self, img_bytes: bytes) -> list:
        img_array = self.preprocess_image(img_bytes)
        result = self.engine.ocr(img_array)
        
        extracted = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text_info = line[1]
                    if isinstance(text_info, (list, tuple)) and len(text_info) == 2:
                        text = text_info[0]
                        confidence = text_info[1]
                        extracted.append({"text": text, "confidence": float(confidence)})
        return extracted
