import io
import base64
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from ..workers.ocr_worker import process_ocr_image, perform_ocr_sync
from ..services.ocr_llm_structurer import OCRLLMStructurer
from ..services.job_queue import celery_app

router = APIRouter(prefix="/ocr", tags=["ocr"])

_structurer = None

# In-memory storage for local OCR results (Redis-free fallback)
LOCAL_OCR_STORAGE = {}

def get_structurer():
    global _structurer
    if _structurer is None:
        _structurer = OCRLLMStructurer(confidence_threshold=0.85)
    return _structurer

@router.post("/process")
async def process_document(file: UploadFile = File(...)):
    """
    Enqueues the OCR processing task to the Celery background queue.
    Falls back to synchronous execution if Redis is unavailable.
    """
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    try:
        img_bytes = await file.read()
        
        # Handle PDF (extract first page)
        if file.content_type == "application/pdf":
            try:
                import fitz # type: ignore
                doc = fitz.open(stream=img_bytes, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")
            except Exception as e:
                raise HTTPException(status_code=422, detail="PDF conversion failed. Ensure PyMuPDF is installed.")

        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
        
        try:
            # Try Celery first
            task = process_ocr_image.delay(encoded_img)
            return {
                "success": True,
                "message": "OCR text extraction job queued.",
                "job_id": task.id
            }
        except Exception as celery_err:
            # Redis likely down, run synchronously as fallback
            job_id = f"local_{uuid.uuid4()}"
            result = perform_ocr_sync(encoded_img)
            LOCAL_OCR_STORAGE[job_id] = result
            
            return {
                "success": True,
                "message": "OCR processing complete (Synchronous Fallback).",
                "job_id": job_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process OCR: {e}")

@router.get("/status/{job_id}")
async def get_ocr_status(job_id: str):
    """
    Frontend poll endpoint to check job status.
    Supports both Celery and local fallback storage.
    """
    task_ready = False
    result = None
    state = "PENDING"

    if job_id.startswith("local_"):
        result = LOCAL_OCR_STORAGE.get(job_id)
        if not result:
            return {"success": False, "status": "FAILED", "error": "Job result not found."}
        task_ready = True
    else:
        try:
            task = celery_app.AsyncResult(job_id)
            task_ready = task.ready()
            if task_ready:
                result = task.result
            state = task.state
        except Exception:
            return {"success": False, "status": "FAILED", "error": "Could not connect to Redis for status."}
    
    if not task_ready:
        return {
            "success": True,
            "status": state,
            "message": "Processing..."
        }
        
    # Task Finished
    if not result or not result.get("success"):
        return {"success": False, "status": "FAILED", "error": result.get("error", "Unknown OCR error") if result else "No Result"}
        
    # Run LLM Structuring on the raw OCR lines
    raw_results = result.get("raw_results", [])
    structurer = get_structurer()
    
    filtered = structurer.filter_by_confidence(raw_results)
    structured_data = structurer.structure_fields(filtered)
    masked_data = structurer.mask_pii(structured_data)
    
    return {
        "success": True,
        "status": "COMPLETED",
        "message": "Please confirm these extracted details before proceeding.",
        "data": structured_data,
        "masked_data_for_agent": masked_data,
        "metrics": {
            "raw_lines": len(raw_results),
            "filtered_lines": len(filtered),
            "discarded_lines": len(raw_results) - len(filtered)
        }
    }
