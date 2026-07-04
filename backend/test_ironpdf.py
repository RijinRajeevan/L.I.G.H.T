import os
import sys

# Run from backend directory, so add current dir to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.utils.form_generator import FormGenerator

def test_ironpdf():
    print("Testing Professional PDF Generation via IronPDF...")
    
    gen = FormGenerator()
    
    test_data = {
        "full_name": "Rohan Nair",
        "aadhaar_number": "1234-5678-9012",
        "dob": "15/05/1995",
        "gender": "Male",
        "address": "Kochi, Kerala, 682001",
        "mobile": "9876543210",
        "reason": "Address correction for Aadhaar"
    }
    
    try:
        filepath, filename = gen.generate("aadhaar_update", test_data)
        
        if os.path.exists(filepath):
            print(f"SUCCESS: PDF generated at {filepath}")
            print(f"Filename: {filename}")
            print(f"Size: {os.path.getsize(filepath)} bytes")
        else:
            print(f"FAILURE: PDF file not found at {filepath}")
            
    except Exception as e:
        print(f"FAILURE: Generation error: {e}")

if __name__ == "__main__":
    test_ironpdf()
