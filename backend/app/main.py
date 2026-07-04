from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import json
import time
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from .api.multimodal import router as multimodal_router
from .services.orchestrator_service import OrchestratorService
from .utils.form_generator import FormGenerator
from .services.scheduler import start_scheduler, shutdown_scheduler

# SlowAPI Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Robust .env loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

# Logging setup for monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server_output_final_v10.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)



# Define the limiter (by IP address)
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up FastAPI application...")
    start_scheduler()
    yield
    # Shutdown actions
    logger.info("Shutting down FastAPI application...")
    shutdown_scheduler()

app = FastAPI(title="NYAYA-VAANI Backend - Production Architecture", lifespan=lifespan)



# Mount Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 2: Error Handling & Logging Middleware Implementation
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Method: {request.method} Path: {request.url.path} Time: {process_time:.4f}s Status: {response.status_code}")
        return response
    except Exception as e:
        # Do not catch RateLimitExceeded or HTTPException here, let FastAPI handlers handle them
        from slowapi.errors import RateLimitExceeded
        if isinstance(e, (RateLimitExceeded, HTTPException)):
            raise e
            
        process_time = time.time() - start_time
        process_time = time.time() - start_time
        import traceback
        tb = traceback.format_exc()
        
        # Write to a dedicated file with UTF-8 encoding
        try:
            with open("critical_errors.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- ERROR ON {request.url.path} at {time.ctime()} ---\n")
                f.write(tb)
                f.write("-" * 50 + "\n")
        except:
            pass # Last resort
            
        logger.error(f"Unhandled Exception on {request.url.path}: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "A critical backend error occurred. Please try again."}
        )

# Include multimodal router
app.include_router(multimodal_router)

# Include OCR router (Phase 3)
from .api.ocr_routes import router as ocr_router
app.include_router(ocr_router)

# Include Observability Metrics (Trust Layer)
from .api.metrics_routes import router as metrics_router
app.include_router(metrics_router)

# Initialize Core Services (Single Instantiation)
orchestrator = OrchestratorService()
form_gen = FormGenerator()

from pydantic import BaseModel, Field
class AnalyzeRequest(BaseModel):
    text: str
    history: list = Field(default_factory=list)  # Prevents mutable default bugs
    session_id: str = "default_session"

@app.get("/")
def read_root():
    return {"message": "NYAYA-VAANI Backend API (FastAPI) is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
@limiter.limit("200/minute", error_message="Rate limit exceeded. Please wait a moment.")
async def analyze_case(request: Request, body: AnalyzeRequest):
    logger.info(f"Received session_id={body.session_id}, history_length={len(body.history)}")
    if not body.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Delegate to clean orchestrator service layer. Fully async workflow.
    result = await orchestrator.analyze_async(body.text, body.history, body.session_id)
    
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=500, detail=result.get("reason", "Analysis Failed"))
    return result

@app.post("/generate-form")
@limiter.limit("5/minute", error_message="You are submitting too many requests. Please slow down and try again later.")
async def generate_form(request: Request, service_type: str = Body(...), user_data: dict = Body(...)):
    """Generate and return a pre-filled PDF form."""
    filepath, filename = form_gen.generate(service_type, user_data)
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf"
    )

import base64
from fastapi import File, UploadFile, Form

def get_local_ip():
    """
    Detects the local network IP address of the machine.
    Useful for generating accessible links in a local network.
    """
    import socket
    try:
        # Create a temporary socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable, just needs to trigger the routing logic
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

@app.post("/generate-qr")
@limiter.limit("20/minute")
async def generate_qr_endpoint(request: Request, data: dict = Body(...)):
    """
    Generates a base64 QR code for sharing instructions or links.
    Replaces localhost/127.0.0.1 with the local network IP for accessibility.
    """
    text = data.get("text", "https://uidai.gov.in/")
    
    # Replace localhost with local IP for cross-device access
    local_ip = get_local_ip()
    text = text.replace("localhost", local_ip).replace("127.0.0.1", local_ip)
    
    import qrcode
    from io import BytesIO
    import base64
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return {"qr_code": f"data:image/png;base64,{img_str}"}

@app.post("/share-sms")
@limiter.limit("5/minute")
async def share_sms_endpoint(request: Request, data: dict = Body(...)):
    """
    Simulates sending instructions and links via SMS.
    """
    phone = data.get("phone")
    message = data.get("message")
    
    if not phone or not message:
        raise HTTPException(status_code=400, detail="Phone and message are required.")
    
    # In a real app, integrate Twilio here
    logger.info(f"SMS SHARED TO {phone}: {message}")
    
    return {"status": "SUCCESS", "msg": f"Instructions sent to {phone}."}

@app.post("/analyze-document")
@limiter.limit("30/minute", error_message="Rate limit exceeded. Please wait a moment.")
async def analyze_document(
    request: Request,
    file: UploadFile = File(...),
    prompt: str = Form(None)
):
    try:
        contents = await file.read()
        mime_type = file.content_type or ""
        
        # Convert document to base64 image
        base64_img = None
        if "pdf" in mime_type.lower() or file.filename.lower().endswith(".pdf"):
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(contents)
            page = pdf[0]
            pil_img = page.render(scale=2).to_pil()
            import io
            buf = io.BytesIO()
            # Convert RGBA to RGB if needed
            if pil_img.mode in ("RGBA", "P"): 
                pil_img = pil_img.convert("RGB")
            pil_img.save(buf, format="JPEG")
            base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
        elif "image" in mime_type.lower() or file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            base64_img = base64.b64encode(contents).decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or an image.")
            
        sys_prompt = "You are a highly capable legal analysis AI specialized in Indian legal documents. The user has uploaded a document which may be in English or Malayalam. Even if the document is in Malayalam, you possess the capability to analyze it, translate the core meaning, and explain it to the user. Your task is to extract the core meaning and explain it in simple, plain layman's terms. Do not use complex legal jargon. Summarize who sent it, what it means, what the user needs to do next, and if it looks urgent. Language Rule: If the document is in Malayalam, provide your explanation in simple Malayalam. If the document is in English, provide your explanation in simple English."
        user_prompt = prompt if prompt else f"Please explain this document ({file.filename}) in simple terms."
        
        # Call local Ollama Llama 3.2 Vision Model
        import http.client
        import json
        
        # Build prompt with system instructions
        full_prompt = f"System: {sys_prompt}\n\nUser: {user_prompt}"
        
        payload = {
            "model": "llama3.2-vision",
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt,
                    "images": [base64_img]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 1024
            }
        }
        
        import urllib.request
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat", 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                analysis = result.get("message", {}).get("content", "")
        except Exception as ollama_err:
            logger.warning(f"Ollama Vision failed, falling back to Groq Vision: {ollama_err}")
            
            # ── FALLBACK: Groq Vision (Reliable Remote Alternative) ──────────
            try:
                from .llm.groq_client import GroqClient
                groq = GroqClient()
                
                # Analyze via Groq's vision model
                analysis = groq.get_completion(
                    prompt=user_prompt,
                    system_prompt=sys_prompt,
                    base64_image=base64_img
                )
                
                if not analysis:
                    raise Exception("Groq Vision returned no analysis.")
                
                return {
                    "status": "SUCCESS",
                    "advice": analysis,
                    "agent_logs": [
                        {"agent": "Neural Vision (Local)", "msg": "Ollama fallback triggered."},
                        {"agent": "Neural Vision (Remote)", "msg": "Successfully analyzed document via Groq Cloud (Llama-3.2-Vision)."}
                    ]
                }
            except Exception as fallback_err:
                logger.error(f"Groq Vision Fallback also failed: {fallback_err}")
                raise HTTPException(status_code=500, detail="Document analysis failed. Both local and remote vision pipelines exhausted.")
        
        if not analysis:
            raise HTTPException(status_code=500, detail="Document analysis failed. Please try again.")
            
        return {
            "status": "SUCCESS",
            "advice": analysis,
            "agent_logs": [{"agent": "Neural Vision", "msg": f"Successfully analyzed '{file.filename}' locally via Llama-3.2-Vision."}]
        }
        
    except Exception as e:
        logger.error(f"Document Analysis Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.get("/download-form/{filename}")
async def download_filled_form(filename: str):
    """
    Serves a filled correction PDF generated by the form-filling agent.

    Filename is a UUID-based safe identifier with no path components.
    """
    # Security: strip any path traversal attempts
    safe_name = os.path.basename(filename)
    if not safe_name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    form_dir = os.path.join(os.path.dirname(__file__), "data", "generated_forms")
    filepath  = os.path.join(form_dir, safe_name)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Form not found or has expired. Please generate it again.")

    return FileResponse(
        path=filepath,
        filename=safe_name,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={safe_name}"},
    )

@app.get("/latest-updates")
@limiter.limit("60/minute", error_message="You are submitting too many requests. Please slow down and try again later.")
async def get_latest_updates(request: Request):
    """Returns latest government procedure updates using internal async file IO."""
    updates_path = "backend/app/data/procedure_updates.json"
    if os.path.exists(updates_path):
        try:
            with open(updates_path, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Updates Error: {e}")
    return {"updates": [], "last_checked": "2026-02-22T00:00:00"}

@app.post("/reset")
@limiter.limit("10/minute", error_message="You are submitting too many requests. Please slow down and try again later.")
async def reset_session(request: Request):
    # Since agent orchestration is now stateless & instantiated per run, 
    # we just acknowledge logic cleanup on the client side.
    return {"status": "Session Reset (Stateless Architecture)"}
