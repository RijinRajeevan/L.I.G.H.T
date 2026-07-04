"""
Multimodal API Router
Handles: Voice Transcription (Groq Whisper), Document OCR (PaddleOCR), Text-to-Speech (edge-tts)
"""
import os
import io
import asyncio
import tempfile
import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq

router = APIRouter(tags=["multimodal"])

# Initialize Groq client for Whisper
_groq_client = None

def get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


# ──────────────────────────────────────────────
# 1. SPEECH TO TEXT — Groq Whisper
# ──────────────────────────────────────────────
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Accept audio (webm / wav / mp3 / m4a) and return transcribed text.
    Supports Malayalam and English natively via Whisper.
    """
    allowed = {"audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg", "application/octet-stream"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: {file.content_type}")

    try:
        audio_bytes = await file.read()
        # Write to temp file (Groq client needs file-like with name)
        suffix = "." + (file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "webm")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcription = get_groq().audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    response_format="text",
                )
            return {"text": transcription, "language_detected": "auto"}
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")



# ──────────────────────────────────────────────
# 3. TEXT TO SPEECH — edge-tts
# ──────────────────────────────────────────────
class SpeakRequest(BaseModel):
    text: str
    lang: str = "en"   # "ml" = Malayalam, "en" = English

VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",      # Indian English (female, natural)
    "ml": "ml-IN-SobhanaNeural",     # Malayalam (female, natural)
}

@router.post("/speak")
async def speak_text(req: SpeakRequest):
    """
    Convert text to speech. Returns MP3 audio stream.
    Supports English (Indian accent) and Malayalam.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(req.text) > 3000:
        raise HTTPException(status_code=400, detail="Text too long (max 3000 chars)")

    try:
        import edge_tts

        voice = VOICE_MAP.get(req.lang, VOICE_MAP["en"])
        
        # Generate speech into memory buffer
        communicate = edge_tts.Communicate(text=req.text, voice=voice)
        
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        
        audio_buffer.seek(0)
        
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )

    except ImportError:
        raise HTTPException(status_code=503, detail="edge-tts not installed. Run: pip install edge-tts")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
