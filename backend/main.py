import io
import uuid
import json
import pytesseract
from typing import List
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.services.search_service import search_utterances
from backend.services.openai_service import classify_intent_with_openai
from backend.services.runbook_evaluator import evaluate_rules
from backend.services.foundry_agent import call_foundry_agent

from backend.agents.classifier import classify_intent
from backend.agents.retriever import retrieve_documents
from backend.agents.validator import validate_document
from backend.agents.escalation import check_escalation
from backend.agents.explainer import explain_steps
from backend.agents.safety import run_safety_check

from backend.routes.uploads import router as uploads_router

MAX_FILE_BYTES = 10 * 1024 * 1024   # 10 MB per file
MAX_EXCERPT_CHARS = 3000            # excerpt chars to send to agent per file

# In-memory chat history
chat_sessions = {}


app = FastAPI(title="Compliance Assistant API")
app.include_router(uploads_router, prefix="/api")


# CORS (frontend -> backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for hackathon / dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_file(upload: UploadFile) -> str:
    """Extract text from file"""
    filename = upload.filename.lower()

    # Always reset pointer before reading
    upload.file.seek(0)
    raw = upload.file.read()
    
    if len(raw) == 0:
        return "ERROR: File is empty"

    # Check file size
    if len(raw) > MAX_FILE_BYTES:
        return f"File {upload.filename} exceeds maximum size of 10 MB."

    # JSON or TXT files
    if filename.endswith((".json", ".txt")):
        try:
            text = raw.decode("utf-8-sig", errors="ignore")
            
            # Try to parse as JSON for pretty formatting
            if filename.endswith(".json"):
                try:
                    parsed = json.loads(text)
                    return json.dumps(parsed, indent=2)
                except json.JSONDecodeError:
                    pass  # Fall through to return raw text
            
            return text
            
        except Exception as e:
            return f"Could not decode file. Error: {str(e)}"

    # PDF
    if filename.endswith(".pdf"):
        text_chunks = []
        pdf_bytes = io.BytesIO(raw)
        
        try:
            reader = PdfReader(pdf_bytes)
            
            # Try text extraction first
            for page_num, page in enumerate(reader.pages):
                t = page.extract_text()
                if t and t.strip():
                    text_chunks.append(t)
            
            # If we got text, return it
            if text_chunks:
                extracted = "\n".join(text_chunks).strip()
                return extracted
            
            # If no text extracted, try OCR on PDF pages            
            try:
                # You need to install: pip install pdf2image
                from pdf2image import convert_from_bytes
                
                # Convert PDF pages to images
                images = convert_from_bytes(raw, dpi=300)
                
                ocr_text_chunks = []
                for i, img in enumerate(images):
                    page_text = pytesseract.image_to_string(img)
                    if page_text.strip():
                        ocr_text_chunks.append(page_text)
                
                if ocr_text_chunks:
                    extracted = "\n\n--- Page Break ---\n\n".join(ocr_text_chunks)
                    return extracted
                else:
                    return "PDF processed but no text found (OCR found no readable text)."
                    
            except ImportError:
                return "Could not extract text from PDF. This appears to be an image-based PDF. To enable OCR, install: pip install pdf2image"
            except Exception as ocr_error:
                return f"Could not extract text from PDF. OCR failed: {str(ocr_error)}"
                
        except Exception as e:
            return f"Could not process PDF file. Error: {str(e)}"

    # DOCX
    if filename.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(raw))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            return f"Could not extract text from DOCX file. Error: {str(e)}"

    # Images
    if filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            image = Image.open(io.BytesIO(raw))
            text = pytesseract.image_to_string(image)
            return text.strip() if text.strip() else "No text found in image."
        except Exception as e:
            return f"Could not extract text from image. Error: {str(e)}"

    return f"Unsupported file format: {filename}"

@app.get("/")
def root():
    return {"status": "backend is running"}

# The orchestrator 
@app.post("/process")
async def process_request(
    text: str = Form(None),
    session_id: str = Form(None),
    files: List[UploadFile] = File(default=[])
):
    DEMO_MODE = True
    text = (text or "").strip()

    # Create session if missing
    if not session_id:
        session_id = str(uuid.uuid4())
        chat_sessions[session_id] = []

    # Append user message if any text was provided
    if text:
        chat_sessions[session_id].append({"role": "user", "content": text})

    # Process uploaded files
    uploaded_file_excerpts = []
    for f in files:
        extracted_text = extract_text_from_file(f)
        uploaded_file_excerpts.append({
            "filename": f.filename,
            "excerpt": extracted_text[:MAX_EXCERPT_CHARS] if extracted_text else None
        })

    # Prepare messages for agent: file excerpts as system messages first
    messages_for_agent = []
    for file_meta in uploaded_file_excerpts:
        if file_meta["excerpt"]:
            messages_for_agent.append({
                "role": "system",
                "content": f"Document {file_meta['filename']} content:\n{file_meta['excerpt']}"
            })
        else:
            messages_for_agent.append({
                "role": "system",
                "content": f"Document {file_meta['filename']} uploaded but could not be parsed. Please ask clarifying questions."
            })

    # Append current session history (user + assistant messages)
    messages_for_agent.extend(chat_sessions[session_id])

    # ---------------------------------------------------------
    # Demo mode: use Foundry agent for simplicity
    # ---------------------------------------------------------
    if DEMO_MODE:
        agent_response = call_foundry_agent(messages_for_agent)
        chat_sessions[session_id].append({"role": "assistant", "content": agent_response})

        return {
            "mode": "demo_foundry_agent",
            "session_id": session_id,
            "input": text,
            "final_output": agent_response,
            "history": chat_sessions[session_id],
            "uploaded_files": uploaded_file_excerpts
        }
    
    # =============================================================
    # Full pipeline
    # =============================================================
    
    # ---------------------
    # Step 1: Classification
    # ---------------------
    raw_intent = classify_intent(text)

    # normalize to string if dict is returned
    if isinstance(raw_intent, dict):
        intent = raw_intent.get("intent", "")
    else:
        intent = raw_intent

    # Ensure intent is always a string
    intent = str(intent)

    # ---------------------
    # Step 2: Azure Search Retrieval
    # ---------------------
    raw_docs = retrieve_documents(intent)

    # normalize to list
    if isinstance(raw_docs, dict):
        docs = raw_docs.get("docs", [])
    else:
        docs = raw_docs or []

    # ---------------------
    # Step 3: Runbook evaluation
    # ---------------------
    context = {
        "intent": intent,
        "docs": docs
    }
    runbook_result = evaluate_rules(context)

    # ---------------------
    # Step 4: Validation
    # ---------------------
    validation_data = validate_document(intent, docs)

    # if the validator returns unexpected formats, normalize:
    if isinstance(validation_data, bool):
        validation = {"checklist_pass": validation_data}
    else:
        validation = validation_data or {}

    # ---------------------
    # Step 5: Escalation
    # ---------------------
    escalation = check_escalation(intent, docs)

    # normalize escalation
    if not isinstance(escalation, bool):
        escalation = False

    # ---------------------
    # Step 6: Explanation
    # ---------------------
    explanation = explain_steps(
        intent=intent,
        docs=docs,
        validation=validation,
        escalation=escalation
    )

    if explanation is None:
        explanation = "No explanation available."

    # ---------------------
    # Step 7: Safety check
    # ---------------------
    safe_output = run_safety_check(explanation)

    return {
        "intent": intent,
        "retrieved_docs": docs,
        "runbook_result": runbook_result,
        "validation": validation,
        "escalation": escalation,
        "explanation": explanation,
        "final_output": safe_output
    }
