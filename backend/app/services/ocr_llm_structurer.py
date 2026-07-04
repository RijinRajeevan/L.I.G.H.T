import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError
from ..llm.groq_client import GroqClient

logger = logging.getLogger(__name__)

class OCRDocumentSchema(BaseModel):
    name: str | None = None
    dob: str | None = None
    aadhaar: str | None = None
    address: str | None = None

class OCRLLMStructurer:
    def __init__(self, confidence_threshold=0.80):
        self.confidence_threshold = confidence_threshold
        self.llm = GroqClient()

    def filter_by_confidence(self, ocr_results: List[Dict]) -> List[Dict]:
        """Drops recognized lines below the confidence threshold."""
        return [item for item in ocr_results if item["confidence"] >= self.confidence_threshold]

    def structure_fields(self, filtered_results: List[Dict]) -> Dict:
        """
        Uses Llama-3-8B via Groq to extract JSON fields from the raw OCR text.
        Replaces brittle regex matching.
        """
        lines = [r["text"] for r in filtered_results]
        full_text = "\n".join(lines)
        
        prompt = f"""
        You are a strict data extraction system.
        Read the following OCR text from an identity document and extract the fields into JSON.
        If a field is not found, output null.
        
        Fields to extract:
        name (string)
        dob (string, format DD/MM/YYYY)
        aadhaar (string, just the 12 digits, no spaces)
        address (string)

        OCR Text:
        {full_text}

        Return ONLY a raw JSON object string. Do not include markdown formatting or explanations.
        """
        
        try:
            # Deterministic, strict extraction
            # We explicitly want temperature=0.0 for structured data
            response_str = self.llm.get_completion(prompt, system_prompt="You are a strict JSON data extractor. Output only raw valid JSON without markdown formatting.", temperature=0.0)
            
            # Clean up potential markdown formatting from LLM
            response_str = response_str.strip()
            if response_str.startswith("```json"):
                response_str = response_str[7:-3].strip()
            elif response_str.startswith("```"):
                response_str = response_str[3:-3].strip()
                
            data = json.loads(response_str)
            
            # Validate with strict Pydantic rules
            validated_data = OCRDocumentSchema(**data).model_dump()
            
            # Legacy mapping for frontend/API compatibility
            return {
                "name": validated_data.get("name"),
                "dob": validated_data.get("dob"),
                "id_number": validated_data.get("aadhaar"),
                "address": validated_data.get("address"),
                "high_confidence_lines": lines
            }
            
        except ValidationError as ve:
            logger.error(f"OCR Pydantic Validation failed: {ve}")
            return self._fallback_struktur(lines)
        except Exception as e:
            logger.error(f"LLM OCR Extraction failed (Network/Parsing): {e}")
            return self._fallback_struktur(lines)

    def _fallback_struktur(self, lines: List[str]) -> Dict:
        return {
            "name": None,
            "dob": None,
            "id_number": None,
            "address": None,
            "high_confidence_lines": lines,
            "extraction_failed": True
        }

    def mask_pii(self, structured_data: Dict) -> Dict:
        """Masks structured IDs before sending to remote LLMs."""
        masked = dict(structured_data)
        if masked.get("id_number"):
            id_str = str(masked["id_number"]).replace(" ", "")
            if len(id_str) >= 4:
                masked["id_number"] = "X" * (len(id_str)-4) + id_str[-4:]
                
        if "high_confidence_lines" in masked:
            masked.pop("high_confidence_lines")

        return masked
