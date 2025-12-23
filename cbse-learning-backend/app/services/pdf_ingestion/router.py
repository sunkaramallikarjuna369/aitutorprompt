from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import os
import json
import hashlib
import logging
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

from ...ai.provider import get_ai_provider
from ...ai.schemas import StudentMode, VisualConfig
from ...utils.auth import get_current_user
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf-ingestion", tags=["PDF Ingestion"])


class PDFFromURLRequest(BaseModel):
    url: str = Field(..., description="URL to download PDF from (e.g., NCERT textbook URL)")
    class_level: str = Field(..., description="CBSE class (e.g., '10')")
    subject: str = Field(..., description="Subject name (e.g., 'Mathematics')")
    chapter: str = Field(..., description="Chapter name (e.g., 'Quadratic Equations')")


class PDFStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class PDFMetadata(BaseModel):
    pdf_id: str
    filename: str
    class_level: str = Field(..., description="CBSE class (e.g., '10')")
    subject: str = Field(..., description="Subject name (e.g., 'Mathematics')")
    chapter: str = Field(..., description="Chapter name (e.g., 'Quadratic Equations')")
    source_url: Optional[str] = None
    status: PDFStatus = PDFStatus.UPLOADED
    uploaded_at: str
    processed_at: Optional[str] = None
    file_size_bytes: int = 0
    page_count: Optional[int] = None
    extracted_topics: List[str] = []
    storage_path: str = ""
    gcs_path: str = Field(default="", description="GCS-compatible path: cbse/class-{level}/{subject}/{chapter}/{filename}")


class PDFUploadResponse(BaseModel):
    pdf_id: str
    message: str
    metadata: PDFMetadata


class ExtractedContent(BaseModel):
    pdf_id: str
    chapter: str
    topics: List[Dict[str, Any]]
    raw_text: Optional[str] = None
    extraction_method: str = "pypdf"


class VisualizationRequest(BaseModel):
    pdf_id: str
    topic_name: str
    student_mode: StudentMode = StudentMode.AVERAGE


class CachedVisualization(BaseModel):
    pdf_id: str
    topic_name: str
    student_mode: StudentMode
    visual_config: Dict[str, Any]
    generated_at: str
    cache_key: str
    gcs_cache_path: str = Field(default="", description="GCS path for cached visualization: cbse/class-{level}/{subject}/{chapter}/visualizations/{topic}/{mode}.json")


# In-memory storage for MVP (replace with GCS/Firestore in production)
pdf_storage: Dict[str, PDFMetadata] = {}
extracted_content_storage: Dict[str, ExtractedContent] = {}
visualization_cache: Dict[str, CachedVisualization] = {}

# Local storage directory for PDFs (MVP)
PDF_STORAGE_DIR = Path("/tmp/cbse_pdfs")
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Cache directory for processed content
CACHE_DIR = Path("/tmp/cbse_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def generate_pdf_id(filename: str, content_hash: str) -> str:
    """Generate a unique PDF ID based on filename and content hash."""
    return hashlib.sha256(f"{filename}:{content_hash}".encode()).hexdigest()[:16]


def generate_cache_key(pdf_id: str, topic_name: str, student_mode: StudentMode) -> str:
    """Generate a cache key for visualization configs."""
    return hashlib.sha256(f"{pdf_id}:{topic_name}:{student_mode}".encode()).hexdigest()[:24]


def sanitize_path_component(name: str) -> str:
    """Sanitize a string for use in file/GCS paths."""
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    sanitized = name.lower().strip()
    sanitized = sanitized.replace(' ', '-')
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '-')
    # Remove multiple consecutive hyphens
    while '--' in sanitized:
        sanitized = sanitized.replace('--', '-')
    return sanitized.strip('-') or 'unknown'


def generate_gcs_path(class_level: str, subject: str, chapter: str, filename: str) -> str:
    """
    Generate a GCS-compatible storage path following the naming strategy:
    
    cbse/class-{level}/{subject}/{chapter}/{filename}
    
    Example:
    cbse/class-10/mathematics/quadratic-equations/chapter.pdf
    
    This structure allows:
    - Easy browsing by class level
    - Organization by subject within each class
    - Chapter-specific content grouping
    - Visualization configs stored alongside source PDFs
    """
    class_dir = f"class-{sanitize_path_component(class_level)}"
    subject_dir = sanitize_path_component(subject)
    chapter_dir = sanitize_path_component(chapter)
    safe_filename = sanitize_path_component(filename.replace('.pdf', '')) + '.pdf'
    
    return f"cbse/{class_dir}/{subject_dir}/{chapter_dir}/{safe_filename}"


def generate_visualization_cache_path(
    class_level: str, 
    subject: str, 
    chapter: str, 
    topic_name: str, 
    student_mode: StudentMode
) -> str:
    """
    Generate a GCS-compatible path for cached visualization configs:
    
    cbse/class-{level}/{subject}/{chapter}/visualizations/{topic}/{mode}.json
    
    Example:
    cbse/class-10/mathematics/quadratic-equations/visualizations/standard-form/dull.json
    """
    class_dir = f"class-{sanitize_path_component(class_level)}"
    subject_dir = sanitize_path_component(subject)
    chapter_dir = sanitize_path_component(chapter)
    topic_dir = sanitize_path_component(topic_name)
    mode_file = f"{student_mode.value}.json"
    
    return f"cbse/{class_dir}/{subject_dir}/{chapter_dir}/visualizations/{topic_dir}/{mode_file}"


def extract_text_from_pdf(pdf_path: Path) -> tuple[str, int]:
    """Extract text from PDF using pypdf. Returns (text, page_count)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        return "\n\n".join(text_parts), len(reader.pages)
    except ImportError:
        logger.warning("pypdf not installed, using mock extraction")
        return "Mock extracted text - install pypdf for real extraction", 1
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF text: {str(e)}")


def parse_topics_from_text(text: str, chapter: str) -> List[Dict[str, Any]]:
    """Parse topics from extracted text. This is a simplified parser for MVP."""
    # For MVP, we'll create a basic structure
    # In production, this would use Gemini to intelligently parse the content
    topics = []
    
    # Simple heuristic: split by common section markers
    sections = text.split("\n\n")
    current_topic = None
    current_content = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Check if this looks like a topic header (simplified heuristic)
        if len(section) < 100 and (
            section.endswith(":") or 
            section[0].isdigit() or
            section.isupper() or
            "introduction" in section.lower() or
            "definition" in section.lower() or
            "formula" in section.lower() or
            "example" in section.lower() or
            "exercise" in section.lower()
        ):
            if current_topic:
                topics.append({
                    "name": current_topic,
                    "content": "\n".join(current_content),
                    "learning_objectives": [f"Understand {current_topic}"]
                })
            current_topic = section.rstrip(":")
            current_content = []
        else:
            current_content.append(section)
    
    # Add last topic
    if current_topic:
        topics.append({
            "name": current_topic,
            "content": "\n".join(current_content),
            "learning_objectives": [f"Understand {current_topic}"]
        })
    
    # If no topics found, create a default one
    if not topics:
        topics.append({
            "name": chapter,
            "content": text[:5000],  # First 5000 chars
            "learning_objectives": [f"Learn about {chapter}"]
        })
    
    return topics


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    class_level: str = Form(..., description="CBSE class (e.g., '10')"),
    subject: str = Form(..., description="Subject name"),
    chapter: str = Form(..., description="Chapter name"),
    source_url: Optional[str] = Form(None, description="Original source URL if downloaded"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a CBSE PDF for processing.
    
    The PDF will be stored and queued for text extraction and topic parsing.
    Use the returned pdf_id to check status and generate visualizations.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read file content
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()
    
    # Generate unique ID
    pdf_id = generate_pdf_id(file.filename, content_hash)
    
    # Check if already uploaded
    if pdf_id in pdf_storage:
        return PDFUploadResponse(
            pdf_id=pdf_id,
            message="PDF already uploaded",
            metadata=pdf_storage[pdf_id]
        )
    
    # Generate GCS-compatible path for future cloud migration
    gcs_path = generate_gcs_path(class_level, subject, chapter, file.filename)
    
    # Save to local storage (MVP) - in production, upload to GCS using gcs_path
    storage_path = PDF_STORAGE_DIR / f"{pdf_id}.pdf"
    with open(storage_path, "wb") as f:
        f.write(content)
    
    # Create metadata
    metadata = PDFMetadata(
        pdf_id=pdf_id,
        filename=file.filename,
        class_level=class_level,
        subject=subject,
        chapter=chapter,
        source_url=source_url,
        status=PDFStatus.UPLOADED,
        uploaded_at=datetime.utcnow().isoformat(),
        file_size_bytes=len(content),
        storage_path=str(storage_path),
        gcs_path=gcs_path
    )
    
    pdf_storage[pdf_id] = metadata
    
    logger.info(f"PDF uploaded: {pdf_id} - {file.filename}")
    
    return PDFUploadResponse(
        pdf_id=pdf_id,
        message="PDF uploaded successfully. Use /process endpoint to extract content.",
        metadata=metadata
    )


@router.post("/from-url", response_model=PDFUploadResponse)
async def download_pdf_from_url(
    request: PDFFromURLRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Download a PDF from a URL (e.g., NCERT textbook) and store it for processing.
    
    Supported sources:
    - NCERT textbooks: https://ncert.nic.in/textbook.php
    - Direct PDF links from educational websites
    
    The PDF will be downloaded, stored, and queued for text extraction.
    Use the returned pdf_id to check status and generate visualizations.
    """
    url = request.url
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    
    # Extract filename from URL
    filename = url.split('/')[-1].split('?')[0]
    if not filename.endswith('.pdf'):
        filename = f"{request.chapter.replace(' ', '_')}.pdf"
    
    try:
        # Download PDF from URL
        logger.info(f"Downloading PDF from: {url}")
        
        # Create request with headers to mimic browser
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,*/*',
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
        
        # Verify it's a PDF
        if not content[:4] == b'%PDF':
            raise HTTPException(status_code=400, detail="Downloaded file is not a valid PDF")
        
        content_hash = hashlib.sha256(content).hexdigest()
        pdf_id = generate_pdf_id(filename, content_hash)
        
        # Check if already uploaded
        if pdf_id in pdf_storage:
            return PDFUploadResponse(
                pdf_id=pdf_id,
                message="PDF already exists (downloaded previously)",
                metadata=pdf_storage[pdf_id]
            )
        
        # Generate GCS-compatible path for future cloud migration
        gcs_path = generate_gcs_path(request.class_level, request.subject, request.chapter, filename)
        
        # Save to local storage (MVP) - in production, upload to GCS using gcs_path
        storage_path = PDF_STORAGE_DIR / f"{pdf_id}.pdf"
        with open(storage_path, "wb") as f:
            f.write(content)
        
        # Create metadata
        metadata = PDFMetadata(
            pdf_id=pdf_id,
            filename=filename,
            class_level=request.class_level,
            subject=request.subject,
            chapter=request.chapter,
            source_url=url,
            status=PDFStatus.UPLOADED,
            uploaded_at=datetime.utcnow().isoformat(),
            file_size_bytes=len(content),
            storage_path=str(storage_path),
            gcs_path=gcs_path
        )
        
        pdf_storage[pdf_id] = metadata
        
        logger.info(f"PDF downloaded from URL: {pdf_id} - {filename} ({len(content)} bytes)")
        
        return PDFUploadResponse(
            pdf_id=pdf_id,
            message="PDF downloaded successfully. Use /process endpoint to extract content.",
            metadata=metadata
        )
        
    except urllib.error.URLError as e:
        logger.error(f"Failed to download PDF from {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download PDF: {str(e)}")
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error downloading PDF from {url}: {e}")
        raise HTTPException(status_code=400, detail=f"HTTP error {e.code}: {e.reason}")
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/ncert-info")
async def get_ncert_info():
    """
    Get information about how to find NCERT textbook PDFs.
    
    NCERT doesn't have a public API, but textbooks are available at:
    https://ncert.nic.in/textbook.php
    
    To get a direct PDF link:
    1. Go to https://ncert.nic.in/textbook.php
    2. Select Class, Subject, and Book
    3. Click on a chapter
    4. Right-click the PDF and copy the link
    5. Use that link with the /from-url endpoint
    """
    return {
        "source": "NCERT",
        "website": "https://ncert.nic.in/textbook.php",
        "instructions": [
            "1. Visit https://ncert.nic.in/textbook.php",
            "2. Select your Class (e.g., Class X)",
            "3. Select Subject (e.g., Mathematics)",
            "4. Select the textbook",
            "5. Click on a chapter to open the PDF",
            "6. Copy the PDF URL from your browser",
            "7. Use the /from-url endpoint with the copied URL"
        ],
        "example_workflow": {
            "step1": "Find PDF URL from NCERT website",
            "step2": "POST /pdf-ingestion/from-url with URL and metadata",
            "step3": "POST /pdf-ingestion/process/{pdf_id} to extract content",
            "step4": "POST /pdf-ingestion/generate-visualization to create visualizations"
        },
        "supported_classes": ["Class I to XII"],
        "supported_subjects": ["Mathematics", "Science", "Social Science", "English", "Hindi", "and more"],
        "note": "NCERT PDFs are text-based and work well with our extraction system"
    }


@router.post("/process/{pdf_id}")
async def process_pdf(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Process an uploaded PDF to extract text and parse topics.
    
    This extracts text from the PDF and identifies topics/sections
    that can be used for visualization generation.
    """
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    metadata = pdf_storage[pdf_id]
    
    if metadata.status == PDFStatus.PROCESSED:
        return {
            "message": "PDF already processed",
            "pdf_id": pdf_id,
            "topics": extracted_content_storage.get(pdf_id, {}).get("topics", [])
        }
    
    # Update status
    metadata.status = PDFStatus.PROCESSING
    
    try:
        # Extract text from PDF
        pdf_path = Path(metadata.storage_path)
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
        raw_text, page_count = extract_text_from_pdf(pdf_path)
        
        # Parse topics from text
        topics = parse_topics_from_text(raw_text, metadata.chapter)
        
        # Store extracted content
        extracted = ExtractedContent(
            pdf_id=pdf_id,
            chapter=metadata.chapter,
            topics=topics,
            raw_text=raw_text[:10000],  # Store first 10k chars for reference
            extraction_method="pypdf"
        )
        extracted_content_storage[pdf_id] = extracted
        
        # Update metadata
        metadata.status = PDFStatus.PROCESSED
        metadata.processed_at = datetime.utcnow().isoformat()
        metadata.page_count = page_count
        metadata.extracted_topics = [t["name"] for t in topics]
        
        logger.info(f"PDF processed: {pdf_id} - {len(topics)} topics found")
        
        return {
            "message": "PDF processed successfully",
            "pdf_id": pdf_id,
            "page_count": page_count,
            "topics_found": len(topics),
            "topics": [{"name": t["name"], "content_preview": t["content"][:200]} for t in topics]
        }
        
    except Exception as e:
        metadata.status = PDFStatus.FAILED
        logger.error(f"PDF processing failed: {pdf_id} - {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/generate-visualization", response_model=CachedVisualization)
async def generate_visualization_from_pdf(
    request: VisualizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a visualization configuration from PDF content using Gemini.
    
    This uses the extracted PDF content to generate a persona-specific
    visualization configuration. Results are cached to minimize AI costs.
    """
    pdf_id = request.pdf_id
    
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if pdf_id not in extracted_content_storage:
        raise HTTPException(
            status_code=400, 
            detail="PDF not processed yet. Call /process endpoint first."
        )
    
    # Check cache first
    cache_key = generate_cache_key(pdf_id, request.topic_name, request.student_mode)
    if cache_key in visualization_cache:
        logger.info(f"Cache hit for visualization: {cache_key}")
        return visualization_cache[cache_key]
    
    # Get extracted content
    extracted = extracted_content_storage[pdf_id]
    
    # Find the requested topic
    topic_content = None
    for topic in extracted.topics:
        if topic["name"].lower() == request.topic_name.lower():
            topic_content = topic
            break
    
    if not topic_content:
        # If exact match not found, use first topic or full content
        topic_content = extracted.topics[0] if extracted.topics else {
            "name": request.topic_name,
            "content": extracted.raw_text or "",
            "learning_objectives": [f"Learn about {request.topic_name}"]
        }
    
    # Generate visualization using AI provider
    ai_provider = get_ai_provider()
    
    try:
        visual_config = await ai_provider.generate_visual_config(
            topic_id=f"{pdf_id}_{request.topic_name}",
            topic_name=topic_content["name"],
            learning_objectives=topic_content.get("learning_objectives", []),
            student_mode=request.student_mode,
            mastery_level=50.0
        )
        
        # Get PDF metadata for GCS path generation
        pdf_metadata = pdf_storage[pdf_id]
        gcs_cache_path = generate_visualization_cache_path(
            pdf_metadata.class_level,
            pdf_metadata.subject,
            pdf_metadata.chapter,
            request.topic_name,
            request.student_mode
        )
        
        # Cache the result
        cached = CachedVisualization(
            pdf_id=pdf_id,
            topic_name=request.topic_name,
            student_mode=request.student_mode,
            visual_config=visual_config.model_dump(),
            generated_at=datetime.utcnow().isoformat(),
            cache_key=cache_key,
            gcs_cache_path=gcs_cache_path
        )
        visualization_cache[cache_key] = cached
        
        # Also save to disk cache for persistence (MVP) - in production, save to GCS using gcs_cache_path
        cache_file = CACHE_DIR / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(cached.model_dump(), f)
        
        logger.info(f"Generated and cached visualization: {cache_key}")
        
        return cached
        
    except Exception as e:
        logger.error(f"Visualization generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/pdfs", response_model=List[PDFMetadata])
async def list_pdfs(
    current_user: User = Depends(get_current_user)
):
    """List all uploaded PDFs."""
    return list(pdf_storage.values())


@router.get("/pdfs/{pdf_id}", response_model=PDFMetadata)
async def get_pdf(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get metadata for a specific PDF."""
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    return pdf_storage[pdf_id]


@router.get("/pdfs/{pdf_id}/topics")
async def get_pdf_topics(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get extracted topics from a processed PDF."""
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if pdf_id not in extracted_content_storage:
        raise HTTPException(
            status_code=400, 
            detail="PDF not processed yet. Call /process endpoint first."
        )
    
    extracted = extracted_content_storage[pdf_id]
    return {
        "pdf_id": pdf_id,
        "chapter": extracted.chapter,
        "topics": extracted.topics
    }


@router.get("/pdfs/{pdf_id}/visualizations")
async def get_pdf_visualizations(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all cached visualizations for a PDF."""
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Find all cached visualizations for this PDF
    cached_visuals = [
        v for v in visualization_cache.values() 
        if v.pdf_id == pdf_id
    ]
    
    return {
        "pdf_id": pdf_id,
        "visualizations": cached_visuals
    }


@router.delete("/pdfs/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a PDF and all associated data."""
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    metadata = pdf_storage[pdf_id]
    
    # Delete file from storage
    pdf_path = Path(metadata.storage_path)
    if pdf_path.exists():
        pdf_path.unlink()
    
    # Delete from memory storage
    del pdf_storage[pdf_id]
    
    if pdf_id in extracted_content_storage:
        del extracted_content_storage[pdf_id]
    
    # Delete cached visualizations
    keys_to_delete = [k for k, v in visualization_cache.items() if v.pdf_id == pdf_id]
    for key in keys_to_delete:
        del visualization_cache[key]
        cache_file = CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
    
    logger.info(f"PDF deleted: {pdf_id}")
    
    return {"message": "PDF and associated data deleted successfully"}


@router.post("/generate-all-visualizations/{pdf_id}")
async def generate_all_visualizations(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate visualizations for all topics and all student modes.
    
    This pre-generates and caches all visualization configs to minimize
    runtime AI calls. Useful for batch processing after PDF upload.
    """
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if pdf_id not in extracted_content_storage:
        raise HTTPException(
            status_code=400, 
            detail="PDF not processed yet. Call /process endpoint first."
        )
    
    extracted = extracted_content_storage[pdf_id]
    pdf_metadata = pdf_storage[pdf_id]
    ai_provider = get_ai_provider()
    
    results = []
    errors = []
    
    for topic in extracted.topics:
        for mode in StudentMode:
            cache_key = generate_cache_key(pdf_id, topic["name"], mode)
            
            # Skip if already cached
            if cache_key in visualization_cache:
                results.append({
                    "topic": topic["name"],
                    "mode": mode,
                    "status": "cached"
                })
                continue
            
            try:
                visual_config = await ai_provider.generate_visual_config(
                    topic_id=f"{pdf_id}_{topic['name']}",
                    topic_name=topic["name"],
                    learning_objectives=topic.get("learning_objectives", []),
                    student_mode=mode,
                    mastery_level=50.0
                )
                
                # Generate GCS cache path
                gcs_cache_path = generate_visualization_cache_path(
                    pdf_metadata.class_level,
                    pdf_metadata.subject,
                    pdf_metadata.chapter,
                    topic["name"],
                    mode
                )
                
                cached = CachedVisualization(
                    pdf_id=pdf_id,
                    topic_name=topic["name"],
                    student_mode=mode,
                    visual_config=visual_config.model_dump(),
                    generated_at=datetime.utcnow().isoformat(),
                    cache_key=cache_key,
                    gcs_cache_path=gcs_cache_path
                )
                visualization_cache[cache_key] = cached
                
                # Save to disk (MVP) - in production, save to GCS using gcs_cache_path
                cache_file = CACHE_DIR / f"{cache_key}.json"
                with open(cache_file, "w") as f:
                    json.dump(cached.model_dump(), f)
                
                results.append({
                    "topic": topic["name"],
                    "mode": mode,
                    "status": "generated"
                })
                
            except Exception as e:
                errors.append({
                    "topic": topic["name"],
                    "mode": mode,
                    "error": str(e)
                })
    
    return {
        "pdf_id": pdf_id,
        "total_topics": len(extracted.topics),
        "total_modes": len(StudentMode),
        "generated": len([r for r in results if r["status"] == "generated"]),
        "cached": len([r for r in results if r["status"] == "cached"]),
        "errors": len(errors),
        "results": results,
        "error_details": errors if errors else None
    }
