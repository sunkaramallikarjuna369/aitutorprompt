from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import random
import uuid
from ...utils.database import db
from ...utils.auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

class StartQuizRequest(BaseModel):
    quiz_type: str = "adaptive"
    question_count: int = Field(default=10, ge=3, le=25)

class AnswerRequest(BaseModel):
    question_id: str
    answer: str
    confidence_level: Optional[int] = Field(default=None, ge=1, le=5)
    response_time_ms: int = Field(default=0, ge=0)

class QuizReport(BaseModel):
    session_id: str
    chapter_id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_taken_seconds: int
    bloom_breakdown: Dict[str, Dict[str, float]]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

@router.post("/chapters/{chapter_id}/start")
async def start_quiz(
    chapter_id: str,
    request: StartQuizRequest,
    current_user: dict = Depends(get_current_user)
):
    chapter = db.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found"
        )
    
    all_questions = db.get_questions_by_chapter(chapter_id)
    if not all_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for chapter {chapter_id}"
        )
    
    if request.quiz_type == "adaptive":
        selected_questions = _select_adaptive_questions(all_questions, request.question_count)
    elif request.quiz_type == "formative":
        selected_questions = _select_formative_questions(all_questions, min(5, request.question_count))
    else:
        selected_questions = random.sample(all_questions, min(len(all_questions), request.question_count))
    
    session = db.create_quiz_session({
        "chapter_id": chapter_id,
        "user_id": current_user["id"],
        "quiz_type": request.quiz_type,
        "questions": [q["id"] for q in selected_questions],
        "current_question_index": 0,
        "current_difficulty": 3,
        "total_score": 0,
        "max_score": sum(q.get("points", 10) for q in selected_questions),
        "bloom_performance": {}
    })
    
    first_question = _prepare_question_for_client(selected_questions[0])
    
    return {
        "session_id": session["id"],
        "chapter_id": chapter_id,
        "quiz_type": request.quiz_type,
        "total_questions": len(selected_questions),
        "current_question": first_question,
        "current_index": 0,
        "time_limit_seconds": selected_questions[0].get("time_limit_seconds", 60)
    }

@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    request: AnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    session = db.get_quiz_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz session {session_id} not found"
        )
    
    if session["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz session"
        )
    
    if session["status"] != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz session is not in progress"
        )
    
    question = db.get_question(request.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {request.question_id} not found"
        )
    
    is_correct = _check_answer(question, request.answer)
    points_earned = question.get("points", 10) if is_correct else 0
    
    attempt = db.create_quiz_attempt({
        "quiz_session_id": session_id,
        "question_id": request.question_id,
        "user_id": current_user["id"],
        "answer_payload": request.answer,
        "is_correct": is_correct,
        "response_time_ms": request.response_time_ms,
        "confidence_level": request.confidence_level,
        "points_earned": points_earned
    })
    
    bloom_level = question.get("bloom_level", "understand")
    bloom_perf = session.get("bloom_performance", {})
    if bloom_level not in bloom_perf:
        bloom_perf[bloom_level] = {"correct": 0, "total": 0}
    bloom_perf[bloom_level]["total"] += 1
    if is_correct:
        bloom_perf[bloom_level]["correct"] += 1
    
    new_difficulty = session["current_difficulty"]
    if session["quiz_type"] == "adaptive":
        if is_correct and request.response_time_ms < question.get("time_limit_seconds", 60) * 500:
            new_difficulty = min(5, new_difficulty + 1)
        elif not is_correct:
            new_difficulty = max(1, new_difficulty - 1)
    
    new_index = session["current_question_index"] + 1
    
    db.update_quiz_session(session_id, {
        "current_question_index": new_index,
        "current_difficulty": new_difficulty,
        "total_score": session["total_score"] + points_earned,
        "bloom_performance": bloom_perf
    })
    
    response = {
        "is_correct": is_correct,
        "points_earned": points_earned,
        "correct_answer": question["correct_answer"],
        "explanation": question.get("explanation", ""),
        "current_score": session["total_score"] + points_earned,
        "questions_remaining": len(session["questions"]) - new_index
    }
    
    if new_index < len(session["questions"]):
        next_question_id = session["questions"][new_index]
        next_question = db.get_question(next_question_id)
        
        if session["quiz_type"] == "adaptive":
            all_questions = db.get_questions_by_chapter(session["chapter_id"])
            suitable_questions = [q for q in all_questions 
                                if q["id"] not in session["questions"][:new_index + 1]
                                and abs(q.get("difficulty", 3) - new_difficulty) <= 1]
            if suitable_questions:
                next_question = random.choice(suitable_questions)
                questions = session["questions"]
                questions[new_index] = next_question["id"]
                db.update_quiz_session(session_id, {"questions": questions})
        
        response["next_question"] = _prepare_question_for_client(next_question)
        response["current_index"] = new_index
        response["time_limit_seconds"] = next_question.get("time_limit_seconds", 60)
    else:
        response["quiz_completed"] = True
    
    return response

@router.post("/{session_id}/finish")
async def finish_quiz(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = db.get_quiz_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz session {session_id} not found"
        )
    
    if session["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz session"
        )
    
    attempts = db.get_attempts_by_session(session_id)
    
    correct_count = sum(1 for a in attempts if a["is_correct"])
    total_time = sum(a.get("response_time_ms", 0) for a in attempts) // 1000
    
    score_pct = (session["total_score"] / session["max_score"] * 100) if session["max_score"] > 0 else 0
    
    bloom_breakdown = {}
    for level, data in session.get("bloom_performance", {}).items():
        if data["total"] > 0:
            bloom_breakdown[level] = {
                "correct": data["correct"],
                "total": data["total"],
                "percentage": round(data["correct"] / data["total"] * 100, 1)
            }
    
    strengths = [level for level, data in bloom_breakdown.items() if data["percentage"] >= 70]
    weaknesses = [level for level, data in bloom_breakdown.items() if data["percentage"] < 50]
    
    recommendations = _generate_recommendations(bloom_breakdown, score_pct)
    
    db.update_quiz_session(session_id, {
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat()
    })
    
    progress = db.get_or_create_progress(current_user["id"], session["chapter_id"])
    quiz_scores = progress.get("quiz_scores", [])
    quiz_scores.append(score_pct)
    avg_score = sum(quiz_scores) / len(quiz_scores)
    
    db.update_progress(current_user["id"], session["chapter_id"], {
        "quiz_scores": quiz_scores,
        "average_quiz_score": avg_score,
        "bloom_performance": bloom_breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses
    })
    
    return {
        "session_id": session_id,
        "chapter_id": session["chapter_id"],
        "total_questions": len(session["questions"]),
        "correct_answers": correct_count,
        "score_percentage": round(score_pct, 1),
        "time_taken_seconds": total_time,
        "bloom_breakdown": bloom_breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations
    }

@router.get("/{session_id}/report")
async def get_quiz_report(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = db.get_quiz_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz session {session_id} not found"
        )
    
    if session["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz session"
        )
    
    attempts = db.get_attempts_by_session(session_id)
    
    detailed_results = []
    for attempt in attempts:
        question = db.get_question(attempt["question_id"])
        if question:
            detailed_results.append({
                "question_id": attempt["question_id"],
                "question_text": question["question_text"],
                "your_answer": attempt["answer_payload"],
                "correct_answer": question["correct_answer"],
                "is_correct": attempt["is_correct"],
                "explanation": question.get("explanation", ""),
                "bloom_level": question.get("bloom_level", "understand"),
                "difficulty": question.get("difficulty", 3),
                "response_time_ms": attempt.get("response_time_ms", 0)
            })
    
    correct_count = sum(1 for a in attempts if a["is_correct"])
    total_time = sum(a.get("response_time_ms", 0) for a in attempts) // 1000
    score_pct = (session["total_score"] / session["max_score"] * 100) if session["max_score"] > 0 else 0
    
    bloom_breakdown = {}
    for level, data in session.get("bloom_performance", {}).items():
        if data["total"] > 0:
            bloom_breakdown[level] = {
                "correct": data["correct"],
                "total": data["total"],
                "percentage": round(data["correct"] / data["total"] * 100, 1)
            }
    
    strengths = [level for level, data in bloom_breakdown.items() if data["percentage"] >= 70]
    weaknesses = [level for level, data in bloom_breakdown.items() if data["percentage"] < 50]
    
    return {
        "session_id": session_id,
        "chapter_id": session["chapter_id"],
        "quiz_type": session["quiz_type"],
        "status": session["status"],
        "started_at": session["started_at"],
        "completed_at": session.get("completed_at"),
        "summary": {
            "total_questions": len(session["questions"]),
            "correct_answers": correct_count,
            "score_percentage": round(score_pct, 1),
            "time_taken_seconds": total_time,
            "total_score": session["total_score"],
            "max_score": session["max_score"]
        },
        "bloom_breakdown": bloom_breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "detailed_results": detailed_results,
        "recommendations": _generate_recommendations(bloom_breakdown, score_pct)
    }

@router.get("/chapters/{chapter_id}/questions")
async def get_chapter_questions(
    chapter_id: str,
    bloom_level: Optional[str] = None,
    difficulty: Optional[int] = None
):
    questions = db.get_questions_by_chapter(chapter_id)
    
    if bloom_level:
        questions = [q for q in questions if q.get("bloom_level") == bloom_level]
    if difficulty:
        questions = [q for q in questions if q.get("difficulty") == difficulty]
    
    return {
        "chapter_id": chapter_id,
        "questions": [_prepare_question_for_client(q) for q in questions],
        "total": len(questions)
    }

def _select_adaptive_questions(questions: List[dict], count: int) -> List[dict]:
    bloom_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
    selected = []
    
    for level in bloom_levels:
        level_questions = [q for q in questions if q.get("bloom_level") == level]
        if level_questions:
            selected.extend(random.sample(level_questions, min(2, len(level_questions))))
    
    remaining = [q for q in questions if q not in selected]
    if len(selected) < count and remaining:
        selected.extend(random.sample(remaining, min(count - len(selected), len(remaining))))
    
    random.shuffle(selected)
    return selected[:count]

def _select_formative_questions(questions: List[dict], count: int) -> List[dict]:
    easy_questions = [q for q in questions if q.get("difficulty", 3) <= 2]
    medium_questions = [q for q in questions if q.get("difficulty", 3) == 3]
    
    selected = []
    if easy_questions:
        selected.extend(random.sample(easy_questions, min(2, len(easy_questions))))
    if medium_questions:
        selected.extend(random.sample(medium_questions, min(count - len(selected), len(medium_questions))))
    
    if len(selected) < count:
        remaining = [q for q in questions if q not in selected]
        selected.extend(random.sample(remaining, min(count - len(selected), len(remaining))))
    
    return selected[:count]

def _prepare_question_for_client(question: dict) -> dict:
    client_question = {
        "id": question["id"],
        "question_text": question["question_text"],
        "type": question["type"],
        "bloom_level": question.get("bloom_level", "understand"),
        "difficulty": question.get("difficulty", 3),
        "points": question.get("points", 10),
        "time_limit_seconds": question.get("time_limit_seconds", 60),
        "hint": question.get("hint")
    }
    
    if question["type"] in ["mcq", "true_false"]:
        options = question.get("options", [])
        client_question["options"] = [{"id": o["id"], "text": o["text"]} for o in options]
    
    return client_question

def _check_answer(question: dict, answer: str) -> bool:
    correct = question["correct_answer"].lower().strip()
    given = answer.lower().strip()
    
    if question["type"] == "numerical":
        try:
            return abs(float(correct) - float(given)) < 0.01
        except ValueError:
            return False
    
    return correct == given

def _generate_recommendations(bloom_breakdown: dict, score_pct: float) -> List[str]:
    recommendations = []
    
    if score_pct >= 80:
        recommendations.append("Excellent work! You have a strong understanding of this chapter.")
        recommendations.append("Try some challenging application problems to deepen your knowledge.")
    elif score_pct >= 60:
        recommendations.append("Good progress! Review the topics where you made mistakes.")
        recommendations.append("Practice more problems to strengthen your understanding.")
    else:
        recommendations.append("Consider reviewing the chapter content before attempting another quiz.")
        recommendations.append("Focus on understanding the basic concepts first.")
    
    weak_levels = [level for level, data in bloom_breakdown.items() if data.get("percentage", 0) < 50]
    
    level_recommendations = {
        "remember": "Review the basic definitions and formulas.",
        "understand": "Work on understanding the concepts through examples.",
        "apply": "Practice solving more problems step by step.",
        "analyze": "Try breaking down complex problems into smaller parts.",
        "evaluate": "Practice comparing different solution methods.",
        "create": "Try creating your own problems and solutions."
    }
    
    for level in weak_levels:
        if level in level_recommendations:
            recommendations.append(f"For {level.title()} level: {level_recommendations[level]}")
    
    return recommendations
