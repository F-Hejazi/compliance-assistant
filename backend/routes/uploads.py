import io
import json
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from docx import Document

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_EXCERPT_CHARS = 3000           # max chars to send to agent per file

router = APIRouter()


def extract_text_from_file(upload: UploadFile) -> str:
    """Extract text content from supported file types"""
    upload.file.seek(0)
    filename = upload.filename.lower()
    raw = upload.file.read()

    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail=f"File {upload.filename} exceeds maximum size of 10 MB.")

    # JSON
    if filename.endswith(".json"):
        try:
            parsed = json.loads(raw.decode("utf-8"))
            return json.dumps(parsed, indent=2)
        except Exception:
            return "Could not parse JSON file."

    # TXT
    if filename.endswith(".txt"):
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return "Could not decode text file."

    # PDF
    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(raw))
            pages = [p.extract_text() or "" for p in reader.pages]
            combined = "\n".join(pages).strip()
            if not combined:
                # fallback to OCR
                image_texts = []
                for page in reader.pages:
                    xobj = page.get("/Resources", {}).get("/XObject", {})
                    for obj in xobj.values():
                        if obj.get("/Subtype") == "/Image":
                            img_data = obj.get_data()
                            image = Image.open(io.BytesIO(img_data))
                            image_texts.append(pytesseract.image_to_string(image))
                combined = "\n".join(image_texts).strip() or "No extractable text in PDF."
            return combined
        except Exception:
            return "Could not extract text from PDF."

    # DOCX
    if filename.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(raw))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return "Could not extract text from DOCX."

    # Images → OCR
    if filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            image = Image.open(io.BytesIO(raw))
            text = pytesseract.image_to_string(image)
            return text.strip() or "OCR found no readable text."
        except Exception:
            return "Could not run OCR on image."

    return f"No extractor implemented for: {filename}"


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Endpoint to upload multiple files and extract text"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    result = []
    for f in files:
        try:
            text = extract_text_from_file(f)
            excerpt = text[:MAX_EXCERPT_CHARS]
            result.append({
                "filename": f.filename,
                "excerpt": excerpt
            })
        except HTTPException as e:
            result.append({
                "filename": f.filename,
                "error": str(e.detail)
            })
        except Exception:
            result.append({
                "filename": f.filename,
                "error": "Unknown error occurred."
            })
    return {"files": result}
