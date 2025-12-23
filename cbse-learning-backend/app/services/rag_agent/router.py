"""
RAG Agent Router - PDF Question Answering and Visualization Generation

This module implements a Retrieval-Augmented Generation (RAG) agent that:
1. Answers questions based on PDF content
2. Generates visualizations to explain concepts from PDFs
3. Adapts responses based on student mode (dull/average/clever)

Architecture (Low-Budget Optimized):
- SQLite FTS5 for text retrieval (free, no external APIs)
- Chunking with overlap for better context
- Caching at multiple levels to minimize AI costs
- Works with both Mock and Vertex AI providers

Cost Optimization:
- FTS5 retrieval: FREE (no embedding API calls)
- Answer caching: Avoids repeated Gemini calls
- Visualization caching: Reuses generated configs
"""

import sqlite3
import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...utils.auth import get_current_user
from ...models.user import User, StudentMode
from ..pdf_ingestion.router import (
    pdf_storage, 
    extracted_content_storage,
    visualization_cache,
    CACHE_DIR
)
from ...ai.provider import get_ai_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag-agent", tags=["RAG Agent"])

# SQLite FTS5 database for text retrieval
RAG_DB_DIR = Path("/tmp/rag_db")
RAG_DB_DIR.mkdir(parents=True, exist_ok=True)

# Cache for RAG answers
rag_answer_cache: Dict[str, Dict[str, Any]] = {}


class QuestionType(str, Enum):
    FACTUAL = "factual"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    APPLICATION = "application"
    EXERCISE = "exercise"


class AskQuestionRequest(BaseModel):
    pdf_id: str = Field(..., description="ID of the processed PDF")
    question: str = Field(..., min_length=3, description="Question to ask about the PDF content")
    student_mode: StudentMode = Field(default=StudentMode.AVERAGE, description="Student learning mode")
    include_visualization: bool = Field(default=True, description="Whether to generate a visualization")
    max_chunks: int = Field(default=5, ge=1, le=10, description="Maximum chunks to retrieve")


class ChunkInfo(BaseModel):
    chunk_id: int
    content: str
    page_number: Optional[int] = None
    score: float


class VisualizationConfig(BaseModel):
    type: str
    title: str
    description: str
    data: Dict[str, Any]
    student_mode: StudentMode
    pedagogical_notes: List[str]


class AskQuestionResponse(BaseModel):
    question: str
    question_type: QuestionType
    answer: str
    citations: List[ChunkInfo]
    visualization: Optional[VisualizationConfig] = None
    student_mode: StudentMode
    cached: bool = False
    pdf_id: str


class IndexStatusResponse(BaseModel):
    pdf_id: str
    indexed: bool
    chunk_count: int
    last_indexed: Optional[str] = None


def get_db_path(pdf_id: str) -> Path:
    """Get the SQLite database path for a PDF."""
    return RAG_DB_DIR / f"{pdf_id}.db"


def create_fts_index(pdf_id: str, chunks: List[Dict[str, Any]]) -> int:
    """
    Create SQLite FTS5 index for PDF chunks.
    
    Args:
        pdf_id: The PDF identifier
        chunks: List of chunks with 'content', 'page_number', 'chunk_index'
        
    Returns:
        Number of chunks indexed
    """
    db_path = get_db_path(pdf_id)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create FTS5 virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            content,
            page_number,
            chunk_index,
            tokenize='porter unicode61'
        )
    """)
    
    # Clear existing data
    cursor.execute("DELETE FROM chunks_fts")
    
    # Insert chunks
    for chunk in chunks:
        cursor.execute(
            "INSERT INTO chunks_fts (content, page_number, chunk_index) VALUES (?, ?, ?)",
            (chunk["content"], chunk.get("page_number", 0), chunk.get("chunk_index", 0))
        )
    
    conn.commit()
    conn.close()
    
    logger.info(f"Created FTS index for PDF {pdf_id} with {len(chunks)} chunks")
    return len(chunks)


def search_chunks(pdf_id: str, query: str, max_results: int = 5) -> List[ChunkInfo]:
    """
    Search for relevant chunks using FTS5.
    
    Args:
        pdf_id: The PDF identifier
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of matching chunks with scores
    """
    db_path = get_db_path(pdf_id)
    
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Clean query for FTS5
    clean_query = re.sub(r'[^\w\s]', ' ', query)
    search_terms = ' OR '.join(clean_query.split())
    
    try:
        cursor.execute("""
            SELECT content, page_number, chunk_index, bm25(chunks_fts) as score
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY score
            LIMIT ?
        """, (search_terms, max_results))
        
        results = []
        for row in cursor.fetchall():
            results.append(ChunkInfo(
                chunk_id=row[2],
                content=row[0],
                page_number=row[1] if row[1] else None,
                score=abs(row[3])
            ))
        
        conn.close()
        return results
        
    except sqlite3.OperationalError as e:
        logger.warning(f"FTS search error: {e}")
        conn.close()
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Overlap between chunks
        
    Returns:
        List of chunk dictionaries
    """
    chunks = []
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    chunk_index = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "page_number": None
                })
                chunk_index += 1
                
                # Keep overlap
                words = current_chunk.split()
                overlap_words = words[-overlap//5:] if len(words) > overlap//5 else []
                current_chunk = ' '.join(overlap_words) + "\n\n" + para + "\n\n"
            else:
                current_chunk = para + "\n\n"
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "chunk_index": chunk_index,
            "page_number": None
        })
    
    return chunks


def classify_question(question: str) -> QuestionType:
    """
    Classify question type using rule-based approach (no AI call).
    """
    question_lower = question.lower()
    
    # Factual/Definition questions
    if any(word in question_lower for word in ['what is', 'define', 'meaning of', 'definition']):
        return QuestionType.FACTUAL
    
    # Procedural questions
    if any(word in question_lower for word in ['how to', 'steps', 'procedure', 'method', 'solve', 'calculate']):
        return QuestionType.PROCEDURAL
    
    # Conceptual questions
    if any(word in question_lower for word in ['why', 'explain', 'reason', 'concept', 'understand']):
        return QuestionType.CONCEPTUAL
    
    # Application questions
    if any(word in question_lower for word in ['example', 'real world', 'application', 'use case', 'practical']):
        return QuestionType.APPLICATION
    
    # Exercise questions
    if any(word in question_lower for word in ['exercise', 'problem', 'question', 'find', 'prove']):
        return QuestionType.EXERCISE
    
    return QuestionType.CONCEPTUAL


def generate_cache_key(pdf_id: str, question: str, student_mode: StudentMode) -> str:
    """Generate a cache key for RAG answers."""
    normalized = question.lower().strip()
    return hashlib.sha256(f"{pdf_id}:{normalized}:{student_mode}".encode()).hexdigest()[:24]


def get_mode_prompt_modifier(student_mode: StudentMode) -> str:
    """Get prompt modifier based on student mode."""
    if student_mode == StudentMode.DULL:
        return """
Explain in very simple terms for a student who struggles with math.
Use everyday examples and analogies.
Break down into small, easy steps.
Use encouraging language.
Avoid complex terminology.
"""
    elif student_mode == StudentMode.CLEVER:
        return """
Provide a comprehensive, advanced explanation.
Include mathematical rigor and proofs where relevant.
Discuss edge cases and exceptions.
Connect to advanced concepts.
Challenge the student with deeper insights.
"""
    else:  # AVERAGE
        return """
Provide a balanced explanation suitable for a typical student.
Include clear examples.
Use standard mathematical terminology with explanations.
Build understanding step by step.
"""


# API Endpoints

@router.post("/index/{pdf_id}", response_model=IndexStatusResponse)
async def index_pdf_for_rag(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Index a processed PDF for RAG queries.
    
    This creates an FTS5 search index from the extracted PDF content.
    Must be called after PDF processing.
    """
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if pdf_id not in extracted_content_storage:
        raise HTTPException(
            status_code=400,
            detail="PDF not processed yet. Call /pdf-ingestion/process first."
        )
    
    extracted = extracted_content_storage[pdf_id]
    
    # Get raw text and chunk it
    raw_text = extracted.raw_text or ""
    
    # Also include topic content
    for topic in extracted.topics:
        raw_text += f"\n\n{topic.get('name', '')}\n{topic.get('content', '')}"
    
    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text content found in PDF"
        )
    
    # Chunk the text
    chunks = chunk_text(raw_text)
    
    # Create FTS index
    chunk_count = create_fts_index(pdf_id, chunks)
    
    return IndexStatusResponse(
        pdf_id=pdf_id,
        indexed=True,
        chunk_count=chunk_count,
        last_indexed=datetime.utcnow().isoformat()
    )


@router.get("/index/{pdf_id}/status", response_model=IndexStatusResponse)
async def get_index_status(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Check if a PDF has been indexed for RAG."""
    db_path = get_db_path(pdf_id)
    
    if not db_path.exists():
        return IndexStatusResponse(
            pdf_id=pdf_id,
            indexed=False,
            chunk_count=0
        )
    
    # Count chunks
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM chunks_fts")
        count = cursor.fetchone()[0]
    except:
        count = 0
    conn.close()
    
    return IndexStatusResponse(
        pdf_id=pdf_id,
        indexed=count > 0,
        chunk_count=count
    )


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question about PDF content using RAG.
    
    This endpoint:
    1. Retrieves relevant chunks from the PDF using FTS5
    2. Generates an answer using the AI provider
    3. Optionally generates a visualization to explain the answer
    4. Caches results to minimize AI costs
    
    The response adapts to the student's learning mode.
    """
    pdf_id = request.pdf_id
    
    # Validate PDF exists and is processed
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if pdf_id not in extracted_content_storage:
        raise HTTPException(
            status_code=400,
            detail="PDF not processed. Call /pdf-ingestion/process first."
        )
    
    # Check if indexed
    db_path = get_db_path(pdf_id)
    if not db_path.exists():
        # Auto-index if not done
        extracted = extracted_content_storage[pdf_id]
        raw_text = extracted.raw_text or ""
        for topic in extracted.topics:
            raw_text += f"\n\n{topic.get('name', '')}\n{topic.get('content', '')}"
        chunks = chunk_text(raw_text)
        create_fts_index(pdf_id, chunks)
    
    # Check cache
    cache_key = generate_cache_key(pdf_id, request.question, request.student_mode)
    if cache_key in rag_answer_cache:
        cached = rag_answer_cache[cache_key]
        cached["cached"] = True
        logger.info(f"RAG cache hit: {cache_key}")
        return AskQuestionResponse(**cached)
    
    # Classify question
    question_type = classify_question(request.question)
    
    # Retrieve relevant chunks
    chunks = search_chunks(pdf_id, request.question, request.max_chunks)
    
    if not chunks:
        # Fallback: use topic content directly
        extracted = extracted_content_storage[pdf_id]
        for i, topic in enumerate(extracted.topics[:3]):
            chunks.append(ChunkInfo(
                chunk_id=i,
                content=topic.get("content", "")[:500],
                score=0.5
            ))
    
    # Build context from chunks
    context = "\n\n---\n\n".join([c.content for c in chunks])
    
    # Get AI provider
    ai_provider = get_ai_provider()
    
    # Generate answer
    mode_modifier = get_mode_prompt_modifier(request.student_mode)
    
    answer_prompt = f"""You are a helpful CBSE mathematics tutor. Answer the student's question based on the provided context.

Context from textbook:
{context}

Student's question: {request.question}

Question type: {question_type.value}

{mode_modifier}

Provide a clear, helpful answer. If the context doesn't contain enough information, say so honestly.
Include relevant formulas or steps if applicable.
"""

    try:
        # Use the AI provider to generate answer
        answer_response = await ai_provider.generate_text(
            prompt=answer_prompt,
            max_tokens=1000
        )
        answer = answer_response if isinstance(answer_response, str) else str(answer_response)
    except AttributeError:
        # Fallback if generate_text not available - use mock response
        answer = f"""Based on the textbook content, here's an explanation for your question about "{request.question}":

{chunks[0].content if chunks else "The concept relates to quadratic equations and their properties."}

Key points to remember:
1. Quadratic equations have the form ax² + bx + c = 0
2. The discriminant (b² - 4ac) determines the nature of roots
3. Real-world applications include projectile motion and optimization problems

This explanation is adapted for {request.student_mode.value} learning mode."""

    # Generate visualization if requested
    visualization = None
    if request.include_visualization:
        try:
            vis_config = await ai_provider.generate_visual_config(
                topic_id=f"{pdf_id}_rag",
                topic_name=request.question[:50],
                learning_objectives=[f"Understand: {request.question}"],
                student_mode=request.student_mode,
                mastery_level=50.0
            )
            visualization = VisualizationConfig(
                type=vis_config.visualization_type,
                title=vis_config.title,
                description=vis_config.description,
                data={
                    "colors": vis_config.color_scheme.model_dump() if hasattr(vis_config.color_scheme, 'model_dump') else {},
                    "interactivity": vis_config.interactivity.model_dump() if hasattr(vis_config.interactivity, 'model_dump') else {},
                },
                student_mode=request.student_mode,
                pedagogical_notes=vis_config.pedagogical_notes
            )
        except Exception as e:
            logger.warning(f"Visualization generation failed: {e}")
            # Provide default visualization
            visualization = VisualizationConfig(
                type="parabola_graph",
                title=f"Visual: {request.question[:30]}...",
                description="Interactive visualization for the concept",
                data={
                    "equation": "y = ax² + bx + c",
                    "default_values": {"a": 1, "b": 0, "c": 0}
                },
                student_mode=request.student_mode,
                pedagogical_notes=["Adjust the sliders to see how the parabola changes"]
            )
    
    # Build response
    response_data = {
        "question": request.question,
        "question_type": question_type,
        "answer": answer,
        "citations": chunks,
        "visualization": visualization,
        "student_mode": request.student_mode,
        "cached": False,
        "pdf_id": pdf_id
    }
    
    # Cache the response
    rag_answer_cache[cache_key] = response_data
    
    # Also save to disk cache
    cache_file = CACHE_DIR / f"rag_{cache_key}.json"
    try:
        with open(cache_file, "w") as f:
            json.dump({
                **response_data,
                "question_type": response_data["question_type"].value,
                "student_mode": response_data["student_mode"].value,
                "citations": [c.model_dump() for c in response_data["citations"]],
                "visualization": response_data["visualization"].model_dump() if response_data["visualization"] else None
            }, f)
    except Exception as e:
        logger.warning(f"Failed to save RAG cache: {e}")
    
    logger.info(f"RAG answer generated for: {request.question[:50]}...")
    
    return AskQuestionResponse(**response_data)


@router.post("/visualize", response_model=VisualizationConfig)
async def generate_visualization_from_question(
    pdf_id: str,
    question: str,
    student_mode: StudentMode = StudentMode.AVERAGE,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a visualization based on a question about PDF content.
    
    This is a simplified endpoint that only generates visualization
    without the full Q&A response.
    """
    if pdf_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Get AI provider
    ai_provider = get_ai_provider()
    
    try:
        vis_config = await ai_provider.generate_visual_config(
            topic_id=f"{pdf_id}_vis",
            topic_name=question[:50],
            learning_objectives=[f"Visualize: {question}"],
            student_mode=student_mode,
            mastery_level=50.0
        )
        
        return VisualizationConfig(
            type=vis_config.visualization_type,
            title=vis_config.title,
            description=vis_config.description,
            data={
                "colors": vis_config.color_scheme.model_dump() if hasattr(vis_config.color_scheme, 'model_dump') else {},
                "interactivity": vis_config.interactivity.model_dump() if hasattr(vis_config.interactivity, 'model_dump') else {},
                "scaffolding": vis_config.scaffolding.model_dump() if hasattr(vis_config.scaffolding, 'model_dump') else {},
            },
            student_mode=student_mode,
            pedagogical_notes=vis_config.pedagogical_notes
        )
    except Exception as e:
        logger.error(f"Visualization generation error: {e}")
        # Return default visualization
        return VisualizationConfig(
            type="parabola_graph",
            title=f"Visualization: {question[:30]}",
            description="Interactive quadratic equation visualization",
            data={
                "equation": "y = ax² + bx + c",
                "default_values": {"a": 1, "b": -2, "c": -3},
                "show_roots": True,
                "show_vertex": True
            },
            student_mode=student_mode,
            pedagogical_notes=[
                "Drag the sliders to change coefficients",
                "Watch how the parabola shape changes",
                "Notice where the curve crosses the x-axis (roots)"
            ]
        )


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """Get RAG cache statistics."""
    return {
        "answer_cache_size": len(rag_answer_cache),
        "visualization_cache_size": len(visualization_cache),
        "cache_directory": str(CACHE_DIR),
        "indexed_pdfs": len(list(RAG_DB_DIR.glob("*.db")))
    }


@router.delete("/cache/{pdf_id}")
async def clear_pdf_cache(
    pdf_id: str,
    current_user: User = Depends(get_current_user)
):
    """Clear all cached data for a specific PDF."""
    # Clear answer cache
    keys_to_delete = [k for k in rag_answer_cache.keys() if pdf_id in k]
    for key in keys_to_delete:
        del rag_answer_cache[key]
    
    # Delete FTS database
    db_path = get_db_path(pdf_id)
    if db_path.exists():
        db_path.unlink()
    
    # Delete disk cache files
    for cache_file in CACHE_DIR.glob(f"rag_*{pdf_id}*.json"):
        cache_file.unlink()
    
    return {
        "message": f"Cache cleared for PDF {pdf_id}",
        "deleted_answers": len(keys_to_delete)
    }
