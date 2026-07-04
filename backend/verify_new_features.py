
import requests
import base64
import os

def test_qr():
    print("Testing /generate-qr...")
    url = "http://localhost:8000/generate-qr"
    payload = {"text": "https://uidai.gov.in/update-aadhar"}
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            qr = data.get("qr_code", "")
            print(f"QR Code generated (starts with {qr[:30]}...)")
            print("✅ QR Test SUCCESS")
        else:
            print(f"❌ QR Test FAILED: {r.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_doc_analysis():
    print("\nTesting /analyze-document (Simulating Fallback)...")
    url = "http://localhost:8000/analyze-document"
    
    # Create a dummy image with text
    from PIL import Image, ImageDraw
    import io
    img = Image.new('RGB', (400, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "This is a test legal document in English.", fill=(0, 0, 0))
    d.text((10, 50), "ഇതൊരു മലയാളം രേഖയാണ്.", fill=(0, 0, 0))
    
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    contents = buf.getvalue()
    
    files = {
        'file': ('test.jpg', contents, 'image/jpeg')
    }
    data = {
        'prompt': 'Analyze this document.'
    }
    
    try:
        # Note: This might trigger the fallback if Ollama is not responding correctly
        print("Sending request to /analyze-document (this may take a moment if OCR falls back)...")
        r = requests.post(url, files=files, data=data, timeout=120)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print("Advice:", result.get("advice", "")[:100] + "...")
            print("Logs:", result.get("agent_logs"))
            print("✅ Doc Analysis Test SUCCESS")
        else:
            print(f"❌ Doc Analysis Test FAILED: {r.status_code}")
            print("Error:", r.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_qr()
    test_doc_analysis()
