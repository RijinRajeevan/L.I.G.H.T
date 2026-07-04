
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image, ImageDraw
import io

def test_paddle():
    print("Initializing PaddleOCR(lang='en')...")
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("Initialization SUCCESS")
        
        # Create test image
        img = Image.new('RGB', (400, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "HELLOWORLD", fill=(0, 0, 0))
        
        img_array = np.array(img)
        print("Running OCR...")
        result = ocr.ocr(img_array)
        print("OCR Result:", result)
        print("✅ PaddleOCR Direct Test SUCCESS")
    except Exception as e:
        print(f"❌ PaddleOCR Direct Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paddle()
