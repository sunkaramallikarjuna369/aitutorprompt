# CBSE Learning Platform

An interactive learning platform for CBSE students featuring adaptive quizzes, real-world applications based on Situated Cognition Theory (SGT), and comprehensive progress tracking.

## Overview

This platform is designed to help Class 10 Mathematics students learn Quadratic Equations through an engaging, interactive experience. The architecture is built to scale to all CBSE classes, subjects, and chapters.

## Architecture

The platform follows a microservices architecture with 9 independent services:

### Backend Services

1. **API Gateway** - Single entry point for frontend, JWT verification, routing
2. **Auth Service** - User authentication, profile management, JWT token generation
3. **Curriculum Service** - CBSE hierarchy management (Board -> Class -> Subject -> Chapter -> Topic)
4. **Content Service** - Learning content delivery with visual configs and SGT flow
5. **Visualization Service** - Dynamic interactive components for quadratic equations
6. **RWAL Service** - Real-World Applications & Situated Cognition Theory implementation
7. **Quiz Service** - Questions, attempts, adaptive difficulty based on Bloom's taxonomy
8. **Progress Service** - Track completion, scores, time-on-task, Bloom level performance
9. **Recommendation Service** - Next steps, review plans, spaced repetition scheduling

### Frontend

- React + TypeScript SPA with Tailwind CSS
- Interactive quadratic equation visualizer with real-time graphing
- Adaptive quiz interface with immediate feedback
- Progress tracking and learning reports

## Situated Cognition Theory (SGT) Implementation

SGT is implemented through a 7-stage learning flow:

1. **Entry Scene** - Real-world scenario (bridge arcs, projectile motion) to contextualize learning
2. **Concept Overview** - Text and graphics introducing the formal quadratic equation
3. **Interactive Parabola** - Sliders for a, b, c coefficients with dynamic graph visualization
4. **Real-World Application Panel** - Daily life examples, industry use cases, career connections
5. **Worked Examples** - Step-by-step solutions with micro-steps
6. **Formative Quiz** - 3-5 questions with immediate feedback
7. **Summative Adaptive Quiz** - Full assessment with difficulty adjustment

### Real-World Applications

Each topic includes:
- Daily life examples (throwing balls, satellite dishes, bridge arches)
- Industry use cases (engineering, physics, economics)
- Career connections (civil engineer, data scientist, game developer)
- Mini project ideas for hands-on learning

## Bloom's Taxonomy Integration

Questions are classified across 6 cognitive levels:

| Level | Description | Example Question Type |
|-------|-------------|----------------------|
| Remember | Recall facts | "What is the standard form of a quadratic equation?" |
| Understand | Explain concepts | "Explain why the discriminant determines the nature of roots" |
| Apply | Use in new situations | "Find the roots of x² - 5x + 6 = 0" |
| Analyze | Draw connections | "Compare factorization and quadratic formula methods" |
| Evaluate | Justify decisions | "Which method is most efficient for this equation?" |
| Create | Produce original work | "Create a real-world problem that uses quadratic equations" |

### Adaptive Quiz Logic

The quiz system adjusts difficulty based on:
- Correctness of previous answers
- Response time (faster correct answers increase difficulty)
- Confidence level (student self-assessment)
- Bloom level performance tracking

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT with bcrypt password hashing
- **Database**: In-memory (MVP) - designed for migration to Cloud SQL/Firestore
- **API Documentation**: OpenAPI/Swagger at `/docs`

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- Poetry (Python package manager)

### Backend Setup

```bash
cd cbse-learning-backend
poetry install
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd cbse-learning-frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile

### Curriculum
- `GET /curriculum/classes` - List all classes
- `GET /curriculum/classes/{classId}/subjects` - Get subjects for a class
- `GET /curriculum/chapters/{chapterId}` - Get chapter with topics
- `GET /curriculum/hierarchy` - Get full curriculum hierarchy

### Content
- `GET /content/topics/{topicId}` - Get topic content
- `GET /content/chapters/{chapterId}/sgt-flow` - Get SGT learning flow

### Visualization
- `POST /visualization/quadratic/analyze` - Analyze quadratic equation
- `POST /visualization/quadratic/plot-points` - Get plot points for graphing
- `POST /visualization/quadratic/solve-steps` - Get step-by-step solution

### Real-World Applications
- `GET /rwal/topics/{topicId}` - Get RWAL scenarios for topic
- `POST /rwal/topics/{topicId}/personalized-examples` - Get personalized examples
- `GET /rwal/chapters/{chapterId}/sgt-entry` - Get SGT entry scene

### Quiz
- `POST /quiz/chapters/{chapterId}/start` - Start a quiz session
- `POST /quiz/{sessionId}/answer` - Submit an answer
- `POST /quiz/{sessionId}/finish` - Finish quiz and get report
- `GET /quiz/{sessionId}/report` - Get quiz report

### Progress
- `GET /progress/me/chapters` - Get progress for all chapters
- `GET /progress/me/chapters/{chapterId}` - Get chapter progress
- `POST /progress/me/chapters/{chapterId}/topic-viewed` - Record topic viewed
- `GET /progress/me/summary` - Get overall progress summary

### Recommendations
- `GET /recommendations/me/next-steps` - Get recommended next steps
- `GET /recommendations/me/review-plan` - Get spaced repetition review plan
- `GET /recommendations/me/learning-path` - Get personalized learning path

## Extending to New Chapters

To add a new chapter:

1. **Add curriculum data** in `cbse-learning-backend/app/utils/database.py`:
   - Add chapter to the chapters dictionary
   - Add topics with learning objectives
   - Add content blocks for each topic

2. **Add questions** in the questions dictionary:
   - Include questions at all Bloom levels
   - Provide hints and explanations

3. **Add RWAL scenarios** in the rwal_scenarios dictionary:
   - Daily life examples
   - Industry use cases
   - Career connections
   - Mini project ideas

4. **Add visual configs** if the chapter requires interactive visualizations

The frontend will automatically display the new content through the existing components.

## Seed Data

The platform includes comprehensive seed data for:
- Class 10 Mathematics - Quadratic Equations
- 7 topics covering all aspects of quadratic equations
- 20+ questions across all Bloom levels
- Multiple RWAL scenarios with real-world applications
- Interactive visualization configs for parabola exploration

## License

MIT License
