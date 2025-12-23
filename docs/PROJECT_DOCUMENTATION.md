# CBSE Learning Platform - Complete Project Documentation

## Project Overview

The CBSE Learning Platform is an AI-driven educational application designed to help Indian students learn CBSE curriculum content through interactive visualizations, adaptive assessments, and personalized learning experiences. The MVP focuses on Class 10 Mathematics - Quadratic Equations.

### Key Features

- **Adaptive Learning**: Content adapts to three student personas (Dull, Average, Clever)
- **Situated Cognition Theory (SGT)**: Real-world applications connect abstract concepts to daily life
- **Bloom's Taxonomy Assessment**: Questions span all six cognitive levels
- **AI-Driven Visualizations**: Dynamic visual explanations generated based on student mode
- **RAG Agent**: Ask questions about PDF content and get contextual answers with visualizations
- **PDF Ingestion Pipeline**: Upload NCERT textbooks and generate learning content
- **Firebase Authentication**: Secure user management with 50K free monthly users

---

## Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + TypeScript | Single Page Application |
| Backend | FastAPI (Python) | Microservices API |
| Database | In-memory (MVP) / Firestore (Production) | Data persistence |
| AI Provider | Vertex AI (Gemini) / Mock Provider | Content generation |
| Authentication | Firebase Auth / JWT | User management |
| Search | SQLite FTS5 | RAG retrieval |
| Storage | Local / GCS | PDF and visualization storage |

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  - Dashboard, Chapter Learning, Quiz, Reports, RAG Agent UI     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                       │
│                    JWT Authentication + CORS                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Auth Service │   │  Curriculum   │   │   Content     │
│               │   │   Service     │   │   Service     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Visualization │   │    RWAL       │   │    Quiz       │
│ Orchestrator  │   │   Service     │   │   Service     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Progress    │   │ Recommendation│   │ PDF Ingestion │
│   Service     │   │   Service     │   │   Service     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐
│  RAG Agent    │   │Firebase Users │
│   Service     │   │   Service     │
└───────────────┘   └───────────────┘
```

---

## Services Reference

### 1. Auth Service (`/auth/*`)

Handles user authentication and profile management.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT token |
| `/auth/me` | GET | Get current user profile |
| `/auth/me` | PUT | Update user profile |

### 2. Curriculum Service (`/curriculum/*`)

Manages CBSE curriculum hierarchy.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/curriculum/classes` | GET | List all classes |
| `/curriculum/classes/{classId}/subjects` | GET | List subjects for a class |
| `/curriculum/subjects/{subjectId}/chapters` | GET | List chapters for a subject |
| `/curriculum/chapters/{chapterId}` | GET | Get chapter details |
| `/curriculum/chapters/{chapterId}/topics` | GET | List topics in a chapter |

### 3. Content Service (`/content/*`)

Serves learning content for topics.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/content/topics/{topicId}` | GET | Get topic content |
| `/content/topics/{topicId}/visual-config` | GET | Get visualization config |

### 4. Visualization Service (`/visualization/*`)

Provides mathematical analysis for visualizations.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/visualization/quadratic/analyze` | POST | Analyze quadratic equation |

### 5. Visualization Orchestrator (`/visualization-orchestrator/*`)

AI-driven visualization generation based on student mode.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/visualization-orchestrator/topics/{topicId}/config` | POST | Generate visual config |
| `/visualization-orchestrator/modes` | GET | List available modes |
| `/visualization-orchestrator/prompt-templates` | GET | Get AI prompt templates |

### 6. RWAL Service (`/rwal/*`)

Real-World Application & Learning - Implements Situated Cognition Theory.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rwal/topics/{topicId}` | GET | Get real-world applications |
| `/rwal/topics/{topicId}/personalized-examples` | POST | Get personalized examples |

### 7. Quiz Service (`/quiz/*`)

Adaptive quiz with Bloom's taxonomy levels.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/quiz/chapters/{chapterId}/start` | POST | Start a quiz session |
| `/quiz/{quizSessionId}/answer` | POST | Submit an answer |
| `/quiz/{quizSessionId}/finish` | POST | Finish quiz and get results |
| `/quiz/{quizSessionId}/report` | GET | Get detailed quiz report |

### 8. Progress Service (`/progress/*`)

Tracks student learning progress.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/progress/me/chapters` | GET | Get all chapter progress |
| `/progress/me/chapters/{chapterId}` | GET | Get specific chapter progress |

### 9. Recommendation Service (`/recommendations/*`)

Provides personalized learning recommendations.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/recommendations/me/next-steps` | GET | Get recommended next steps |
| `/recommendations/me/review-plan` | GET | Get spaced repetition plan |

### 10. PDF Ingestion Service (`/pdf-ingestion/*`)

Processes NCERT PDFs and generates visualizations.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdf-ingestion/upload` | POST | Upload PDF file |
| `/pdf-ingestion/from-url` | POST | Download PDF from URL |
| `/pdf-ingestion/process/{pdf_id}` | POST | Extract text and topics |
| `/pdf-ingestion/generate-visualization` | POST | Generate visualization |
| `/pdf-ingestion/generate-all-visualizations/{pdf_id}` | POST | Batch generate all |
| `/pdf-ingestion/pdfs` | GET | List all PDFs |
| `/pdf-ingestion/pdfs/{pdf_id}` | GET | Get PDF details |
| `/pdf-ingestion/ncert-info` | GET | NCERT download instructions |

### 11. RAG Agent Service (`/rag-agent/*`)

PDF Question Answering with visualization generation.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rag-agent/index/{pdf_id}` | POST | Index PDF for RAG |
| `/rag-agent/index/{pdf_id}/status` | GET | Check index status |
| `/rag-agent/ask` | POST | Ask question about PDF |
| `/rag-agent/visualize` | POST | Generate visualization |
| `/rag-agent/cache/stats` | GET | View cache statistics |
| `/rag-agent/cache/{pdf_id}` | DELETE | Clear PDF cache |

### 12. Firebase Users Service (`/firebase-users/*`)

Firebase-based user management.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/firebase-users/status` | GET | Check Firebase status |
| `/firebase-users/create` | POST | Create user |
| `/firebase-users/me` | GET | Get current user |
| `/firebase-users/{uid}` | GET | Get user by UID |
| `/firebase-users/{uid}` | PUT | Update user |
| `/firebase-users/{uid}` | DELETE | Delete user |
| `/firebase-users/password-reset` | POST | Generate reset link |
| `/firebase-users/set-student-mode` | POST | Set learning mode |
| `/firebase-users/set-class` | POST | Set student class |

---

## Student Persona Modes

The platform adapts content based on three student personas:

### Dull Mode
- **Target**: Students struggling with mathematics
- **Content Style**: Simplified language, step-by-step explanations
- **Visualizations**: High contrast colors, slow animations (0.5x speed)
- **Scaffolding**: Maximum support with real-world metaphors (ball trajectory, bridge arches)
- **AI Prompt**: "Generate a simplified, high-scaffolding visual configuration for a 14-year-old struggling with math..."

### Average Mode
- **Target**: Students with moderate understanding
- **Content Style**: Balanced procedural explanations
- **Visualizations**: Standard mathematical color coding, medium complexity
- **Scaffolding**: Moderate support with discriminant shown
- **AI Prompt**: "Generate a balanced procedural visualization focusing on the relationship between variables..."

### Clever Mode
- **Target**: Advanced students seeking challenges
- **Content Style**: Concise, mathematical notation, advanced concepts
- **Visualizations**: Abstract, complex, fast animations (1.5x speed)
- **Scaffolding**: Minimal, includes sandbox mode for experimentation
- **AI Prompt**: "Generate a complex, abstract visualization including discriminant's impact on complex roots..."

---

## Situated Cognition Theory (SGT) Implementation

SGT connects abstract mathematical concepts to real-world applications:

### Learning Flow

1. **Entry Scene**: Show authentic real-world scenario (bridge design, projectile motion)
2. **Concept Introduction**: Connect formal equation to the scene
3. **Interactive Exploration**: Manipulate parameters and see effects
4. **Real-World Applications**: Daily life examples, industry use cases
5. **Career Connections**: How professionals use these concepts
6. **Mini Projects**: Hands-on application ideas

### RWAL Content Categories

| Category | Examples |
|----------|----------|
| Daily Life | Ball trajectory, water fountains, satellite dishes |
| Industry | Bridge engineering, architecture, physics simulations |
| Careers | Civil engineer, game developer, data scientist |
| Projects | Design a parabolic reflector, model projectile motion |

---

## Bloom's Taxonomy Assessment

Quiz questions span all six cognitive levels:

| Level | Description | Example Question Type |
|-------|-------------|----------------------|
| Remember | Recall facts | "What is the quadratic formula?" |
| Understand | Explain concepts | "Why does the discriminant determine root type?" |
| Apply | Use in new situations | "Solve: x² + 5x + 6 = 0" |
| Analyze | Break down components | "How does changing 'a' affect the parabola?" |
| Evaluate | Make judgments | "Which method is most efficient for this equation?" |
| Create | Produce new work | "Design a quadratic equation with roots at 2 and -3" |

### Adaptive Quiz Algorithm

1. Start with mixed difficulty questions
2. Track correctness and response time
3. Adjust difficulty based on performance
4. Provide immediate feedback with explanations
5. Generate detailed report with Bloom level analysis

---

## RAG Agent Architecture

The RAG (Retrieval-Augmented Generation) Agent enables PDF-based Q&A:

### Pipeline

```
Question → Classification → Retrieval → Generation → Response
    │           │              │            │           │
    │           │              │            │           └─ Answer + Visualization
    │           │              │            └─ AI generates contextual answer
    │           │              └─ SQLite FTS5 retrieves relevant chunks
    │           └─ Rule-based classification (no AI cost)
    └─ User asks about PDF content
```

### Question Types

| Type | Description | Example |
|------|-------------|---------|
| Factual | Direct information retrieval | "What is the quadratic formula?" |
| Conceptual | Understanding relationships | "Why do quadratic equations have at most 2 roots?" |
| Procedural | Step-by-step processes | "How do I complete the square?" |
| Application | Real-world usage | "How is this used in physics?" |
| Exercise | Practice problems | "Solve x² - 4x + 3 = 0" |

### Cost Optimization

- **SQLite FTS5**: Free full-text search (no embedding API costs)
- **Rule-based Classification**: No AI calls for question type detection
- **Multi-level Caching**: 
  - Level 1: Processed PDF chunks
  - Level 2: Retrieval results per question
  - Level 3: Final answers per (question, mode)
  - Level 4: Visualizations per (question, mode)

---

## PDF Ingestion Pipeline

### GCS Naming Strategy

```
gs://bucket-name/
  cbse/
    class-10/
      mathematics/
        quadratic-equations/
          chapter.pdf
          visualizations/
            standard-form/
              dull.json
              average.json
              clever.json
            discriminant/
              dull.json
              average.json
              clever.json
    class-9/
      science/
        ...
```

### Processing Workflow

1. **Upload**: PDF file or NCERT URL
2. **Extract**: Text extraction using PyPDF2
3. **Parse**: Identify topics and sections
4. **Chunk**: Split into 800-1200 character chunks with overlap
5. **Index**: Create SQLite FTS5 index for RAG
6. **Generate**: Create visualizations for each topic and mode
7. **Cache**: Store results to avoid repeated AI calls

---

## AI Provider Abstraction

The platform supports multiple AI providers:

### Mock Provider (Default)
- **Cost**: Free
- **Use Case**: Development, testing, demos
- **Behavior**: Returns deterministic, pedagogically appropriate responses
- **Configuration**: `AI_PROVIDER=mock`

### Vertex AI Provider (Production)
- **Cost**: Pay per use (~$0.001 per 1K tokens)
- **Use Case**: Production with real AI responses
- **Model**: Gemini 1.5 Flash
- **Configuration**: 
  ```
  AI_PROVIDER=vertex
  VERTEX_AI_PROJECT=your-project-id
  VERTEX_AI_LOCATION=us-central1
  ```

### Fallback Behavior

If Vertex AI fails (quota, network, etc.), the system automatically falls back to the Mock provider to ensure uninterrupted service.

---

## Data Models

### User Profile

```python
{
    "id": "user-uuid",
    "email": "student@example.com",
    "name": "Student Name",
    "class_level": "10",
    "school": "Example School",
    "learning_style": "visual",
    "student_mode": "average",  # dull, average, clever
    "created_at": "2024-12-01T00:00:00Z"
}
```

### Chapter Progress

```python
{
    "user_id": "user-uuid",
    "chapter_id": "chapter-uuid",
    "status": "in_progress",  # not_started, in_progress, completed
    "progress_pct": 65,
    "topics_completed": ["topic-1", "topic-2"],
    "quiz_scores": [85, 90],
    "bloom_performance": {
        "remember": 90,
        "understand": 85,
        "apply": 75,
        "analyze": 70,
        "evaluate": 60,
        "create": 50
    },
    "time_spent_minutes": 120
}
```

### Quiz Session

```python
{
    "id": "quiz-uuid",
    "user_id": "user-uuid",
    "chapter_id": "chapter-uuid",
    "questions": [...],
    "answers": [...],
    "score": 85,
    "bloom_breakdown": {...},
    "started_at": "2024-12-01T10:00:00Z",
    "completed_at": "2024-12-01T10:30:00Z"
}
```

### RAG Query

```python
{
    "pdf_id": "pdf-uuid",
    "question": "What is the quadratic formula?",
    "question_type": "factual",
    "student_mode": "average",
    "answer": "The quadratic formula is...",
    "citations": [
        {
            "chunk_id": 5,
            "content": "For any quadratic equation...",
            "page_number": 3,
            "score": 0.95
        }
    ],
    "visualization": {...},
    "cached": false
}
```

---

## Frontend Pages

### 1. Login/Register (`/login`)
- Email/password authentication
- Registration with class selection
- JWT token management

### 2. Dashboard (`/dashboard`)
- Class/Subject/Chapter navigation
- Progress overview
- Quick access to recent chapters

### 3. Chapter Learning (`/chapter/:id/learn`)
- **Left Panel**: Topic navigation
- **Center Panel**: Content viewer with tabs
  - Content: Text explanations
  - Visualizer: Interactive quadratic graph
  - Real-World: SGT applications
- **Right Panel**: Progress and quick actions

### 4. Quiz (`/chapter/:id/quiz`)
- Adaptive question display
- Progress bar
- Immediate feedback
- Bloom level indicators

### 5. Reports (`/reports`)
- Overall progress charts
- Bloom taxonomy performance
- Recommendations

### 6. RAG Agent (`/rag-agent`)
- PDF selection
- Learning mode selector
- Question input
- Answer display with citations
- Visualization display

---

## Environment Variables

### Backend

```bash
# AI Provider
AI_PROVIDER=mock                    # mock or vertex
VERTEX_AI_PROJECT=your-project      # GCP project ID
VERTEX_AI_LOCATION=us-central1      # GCP region

# Firebase (optional)
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json

# Application
APP_ENV=development                 # development or production
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
PDF_STORAGE_PATH=/tmp/cbse_pdfs
CACHE_PATH=/tmp/cbse_cache
RAG_DB_PATH=/tmp/rag_db
```

### Frontend

```bash
VITE_API_URL=http://localhost:8000
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry (Python package manager)

### Backend Setup

```bash
cd cbse-learning-backend
poetry install
poetry run fastapi dev app/main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend Setup

```bash
cd cbse-learning-frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### Test Credentials

- Email: `user`
- Password: `dd058af30a635609e894c13b4e524841`

---

## Deployment

See `docs/LOW_BUDGET_DEPLOYMENT_GUIDE.md` for detailed GCP deployment instructions.

### Quick Deploy (Cloud Run)

```bash
# Build and push image
docker build -t asia-south1-docker.pkg.dev/PROJECT/cbse-app/backend:v1 .
docker push asia-south1-docker.pkg.dev/PROJECT/cbse-app/backend:v1

# Deploy to Cloud Run
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/PROJECT/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=2
```

---

## Cost Estimates

### Free Tier (0-1000 INR/month)
- Cloud Run: Scales to zero
- Mock AI provider
- In-memory database
- Good for: Demos, testing

### Basic (1000-3000 INR/month)
- Cloud Run with Firestore
- Limited Vertex AI usage
- Good for: Small school (50-100 students)

### Production (3000-10000 INR/month)
- Cloud SQL for relational data
- Memorystore for caching
- Full Vertex AI features
- Good for: Medium school (100-500 students)

---

## Extending the Platform

### Adding a New Chapter

1. Add chapter data to curriculum service seed data
2. Add topic content to content service
3. Add RWAL scenarios for SGT
4. Add quiz questions with Bloom levels
5. Upload chapter PDF for RAG

### Adding a New Subject

1. Create subject entry in curriculum hierarchy
2. Define chapter structure
3. Create visualization templates for subject-specific concepts
4. Add subject-specific RWAL scenarios

### Adding a New Class

1. Add class to curriculum service
2. Define subjects for the class
3. Follow subject/chapter addition process

---

## Security Considerations

- JWT tokens for API authentication
- Firebase Auth for production user management
- No credentials in code or git
- CORS configured for frontend origin
- Input validation on all endpoints
- Rate limiting recommended for production

---

## Troubleshooting

### Common Issues

1. **CORS errors**: Check backend CORS configuration
2. **JWT expired**: Re-login to get new token
3. **AI provider errors**: Check credentials and quotas
4. **PDF processing fails**: Ensure PDF is text-based, not scanned

### Logs

```bash
# Local backend logs
poetry run fastapi dev app/main.py

# Cloud Run logs
gcloud run services logs read cbse-learning-app --region=asia-south1
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

---

## License

This project is for educational purposes. NCERT content is owned by NCERT/CBSE.

---

## Contact

For questions or support, please open an issue on GitHub.

---

*Last updated: December 2024*
