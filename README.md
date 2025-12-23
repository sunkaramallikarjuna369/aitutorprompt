# CBSE Learning Platform

An interactive learning platform for CBSE students featuring AI-driven adaptive visualizations, real-world applications based on Situated Cognition Theory (SGT), and comprehensive progress tracking with Bloom's taxonomy integration.

## Overview

This platform is designed to help Class 10 Mathematics students learn Quadratic Equations through an engaging, interactive experience. The architecture is built to scale to all CBSE classes, subjects, and chapters.

Key features include:
- AI-driven visualization orchestration with student persona modes (Dull/Average/Clever)
- Vertex AI (Gemini) integration for content generation
- Situated Cognition Theory (SGT) implementation for real-world learning
- Adaptive quizzes based on Bloom's taxonomy
- Comprehensive progress tracking and recommendations

## Architecture

The platform follows a microservices architecture with 10 independent services:

### Backend Services

1. **API Gateway** - Single entry point for frontend, JWT verification, routing
2. **Auth Service** - User authentication, profile management, JWT token generation
3. **Curriculum Service** - CBSE hierarchy management (Board -> Class -> Subject -> Chapter -> Topic)
4. **Content Service** - Learning content delivery with visual configs and SGT flow
5. **Visualization Service** - Dynamic interactive components for quadratic equations
6. **Visualization Orchestrator** - AI-driven visualization configuration with student persona modes
7. **RWAL Service** - Real-World Applications & Situated Cognition Theory implementation
8. **Quiz Service** - Questions, attempts, adaptive difficulty based on Bloom's taxonomy
9. **Progress Service** - Track completion, scores, time-on-task, Bloom level performance
10. **Recommendation Service** - Next steps, review plans, spaced repetition scheduling

### Frontend

- React + TypeScript SPA with Tailwind CSS
- Interactive quadratic equation visualizer with real-time graphing
- Student mode selector for personalized learning experience
- Adaptive quiz interface with immediate feedback
- Progress tracking and learning reports

## AI-Driven Visualization Orchestrator

The platform includes an AI-driven visualization orchestrator that generates personalized visual configurations based on student learning modes. This service uses Vertex AI (Gemini) in production or a mock provider for local development.

### Student Persona Modes

The platform supports three learning modes that adapt the visualization and content delivery:

| Mode | Target Audience | Characteristics |
|------|-----------------|-----------------|
| **Dull** | Students struggling with math | Simplified visuals, high scaffolding, real-world metaphors, slow animations |
| **Average** | Students with foundational understanding | Balanced procedural visualizations, standard color coding, medium scaffolding |
| **Clever** | Advanced students seeking challenges | Complex abstract visualizations, sandbox mode, minimal scaffolding |

### AI Prompt Templates

The visualization orchestrator uses specific prompts for each student mode:

#### Dull Mode Prompt
```
Generate a simplified, high-scaffolding visual configuration for a 14-year-old struggling 
with math. Use concrete real-world metaphors (e.g., a ball's path). Slow down animation 
speeds and use bright, high-contrast visual cues for the X and Y axis.
```

#### Average Mode Prompt
```
Generate a balanced procedural visualization. Focus on the relationship between the 
quadratic formula variables and the parabola's movement. Use standard mathematical 
color coding.
```

#### Clever Mode Prompt
```
Generate a complex, abstract visualization. Include the discriminant's impact on complex 
roots and 3D transformations. Provide a 'sandbox' mode where the student can stress-test 
the limits of the equation.
```

### Visual Configuration Output

The AI generates a JSON configuration that controls:
- Animation speed, easing, and duration
- Axis colors and emphasis levels
- Color schemes (primary, secondary, background, accent)
- Scaffolding level (hints, step numbers, key point highlighting)
- Interactivity options (sandbox mode, sliders, zoom, drag)
- Advanced features (discriminant, complex roots, 3D transformations)
- Pedagogical notes for the student

### API Endpoints

- `POST /visualization-orchestrator/topics/{topicId}/config` - Generate visual config for a topic
- `GET /visualization-orchestrator/topics/{topicId}/config/preview` - Preview all three mode configs
- `POST /visualization-orchestrator/topics/{topicId}/worked-example` - Generate worked example
- `GET /visualization-orchestrator/prompt-templates` - Get all prompt templates
- `GET /visualization-orchestrator/modes` - Get available learning modes

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

## GCP Deployment

The platform includes multiple deployment options for different budgets and skill levels.

### Quick Start: Low-Budget Deployment (Recommended for Beginners)

**Budget: 1000 INR/month (~$12 USD) or FREE using GCP free tier**

If you're new to GCP or have a limited budget, start here:

1. **[Low-Budget Deployment Guide](docs/LOW_BUDGET_DEPLOYMENT_GUIDE.md)** - Step-by-step instructions for complete beginners
2. **[Cost Optimization Guide](docs/COST_OPTIMIZATION.md)** - Tips to minimize costs and stay within budget
3. **[Budget Estimate](docs/BUDGET_ESTIMATE.md)** - Detailed cost breakdown for different scales

The low-budget approach uses:
- Single Cloud Run service (scales to zero = no cost when idle)
- In-memory database (for demos) or Firestore (for persistence)
- Mock AI provider (no Vertex AI costs)
- Simplified CI/CD with Cloud Build

### Full Production Deployment

For larger deployments with more features, use the Terraform configuration:

#### Prerequisites

- GCP Project with billing enabled
- Terraform 1.0+
- gcloud CLI configured

#### Infrastructure Setup

```bash
cd infra/terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and apply
terraform init
terraform plan
terraform apply
```

This creates:
- Cloud Run services for backend
- Cloud SQL PostgreSQL instance
- Firestore database (Native mode)
- Redis instance for caching
- Pub/Sub topics for async events
- Cloud Storage buckets for media and frontend
- Artifact Registry for container images
- Secret Manager for sensitive configuration

### CI/CD with Cloud Build

The `infra/cloudbuild/cloudbuild.yaml` file defines the CI/CD pipeline:

1. Run backend tests
2. Build and test frontend
3. Build Docker image for backend
4. Push to Artifact Registry
5. Deploy backend to Cloud Run
6. Deploy frontend to Cloud Storage

To trigger a build:

```bash
gcloud builds submit --config=infra/cloudbuild/cloudbuild.yaml
```

### Environment Variables

For Vertex AI integration, set:
- `AI_PROVIDER=vertex` (default is `mock` for local development)
- `VERTEX_AI_PROJECT=your-project-id`
- `VERTEX_AI_LOCATION=us-central1`

## License

MIT License
