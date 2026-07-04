from ..llm.groq_client import GroqClient
import re

class LanguageAgent:
    def __init__(self):
        self.llm = GroqClient()
        
    def is_malayalam(self, text):
        # Malayalam Unicode range is U+0D00 to U+0D7F
        return any('\u0d00' <= char <= '\u0d7f' for char in text)

    def translate(self, text, target_language="English"):
        if not text:
            return ""
            
        is_already_target = False
        if target_language.lower() == "english" and text.isascii():
            is_already_target = True
        elif target_language.lower() == "malayalam" and self.is_malayalam(text):
            is_already_target = True
            
        if is_already_target:
            return text

        prompt = f"""Translate the following text to {target_language}.
        Text: "{text}"
        
        Guidelines:
        - Return ONLY the translated text.
        - Preserve proper nouns like "Aadhaar", "Akshaya", "Kerala".
        - Use formal language suitable for a government service kiosk.
        """
        
        response = self.llm.get_completion(prompt)
        return response.strip() if response else text

    def detect_language(self, text):
        if self.is_malayalam(text):
            return "Malayalam"
        if text.isascii():
            return "English"
            
        prompt = f"""Detect the language of the following text: "{text}".
        Return ONLY the language name (Malayalam or English). If unsure, reply 'English'.
        """
        response = self.llm.get_completion(prompt)
        return response.strip() if response else "English"

if __name__ == "__main__":
    agent = LanguageAgent()
    print(agent.translate("എനിക്ക് ഒരു വരുമാന സർട്ടിഫിക്കറ്റ് വേണം", "English"))
