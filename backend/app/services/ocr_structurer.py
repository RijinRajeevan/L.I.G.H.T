import re
from typing import List, Dict

class OCRStructurer:
    def __init__(self, confidence_threshold=0.80):
        self.confidence_threshold = confidence_threshold

    def filter_by_confidence(self, ocr_results: List[Dict]) -> List[Dict]:
        """
        Drops any recognized line that falls below the confidence threshold.
        """
        return [item for item in ocr_results if item["confidence"] >= self.confidence_threshold]

    def structure_fields(self, filtered_results: List[Dict]) -> Dict:
        """
        Regex based basic structuring for MVP.
        Finds common fields like Name, DOB, Aadhaar, IDs, etc.
        """
        structured = {
            "name": None,
            "dob": None,
            "id_number": None,
            "high_confidence_lines": []
        }
        
        lines = [r["text"] for r in filtered_results]
        full_text = " ".join(lines)
        
        # Simple Regex Patterns
        # Aadhaar: 4 digits space 4 digits space 4 digits (or just 12 digits)
        aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', full_text)
        if aadhaar_match:
            structured["id_number"] = aadhaar_match.group(0).strip()
            
        # DOB pattern DD/MM/YYYY or DD-MM-YYYY
        dob_match = re.search(r'\b(\d{2}[-/]\d{2}[-/]\d{4})\b', full_text)
        if dob_match:
            structured["dob"] = dob_match.group(1)
            
        # Mock Name pattern
        name_match = re.search(r'Name\s*[:\-]\s*([A-Za-z\s]+)', full_text, re.IGNORECASE)
        if name_match:
            structured["name"] = name_match.group(1).strip()
            
        structured["high_confidence_lines"] = lines
        return structured

    def mask_pii(self, structured_data: Dict) -> Dict:
        """
        Masks structured IDs before sending to LLM.
        Prevents raw user data leaking to third-party endpoints.
        """
        masked = dict(structured_data)
        if masked.get("id_number"):
            id_str = masked["id_number"].replace(" ", "")
            if len(id_str) >= 4:
                masked["id_number"] = "X" * (len(id_str)-4) + id_str[-4:]
                
        # To mask dates or names, further logic can be added here.
        # Removing raw lines so LLM doesn't see them either.
        if "high_confidence_lines" in masked:
            # Maybe keep only non-PII lines, but to be sure we just pop it.
            masked.pop("high_confidence_lines")

        return masked
