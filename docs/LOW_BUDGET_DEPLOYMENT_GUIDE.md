# Low-Budget GCP Deployment Guide (1000 INR/month)

This guide is designed for complete GCP beginners who want to deploy the CBSE Learning Platform with a budget of approximately 1000 INR (~$12 USD) per month. We'll use an incremental approach, deploying one component at a time.

## Budget Strategy

With 1000 INR/month, we'll leverage GCP's generous free tier:

| Service | Free Tier | Our Usage |
|---------|-----------|-----------|
| Cloud Run | 2 million requests/month, 360,000 GB-seconds | Single service, scales to zero |
| Cloud Storage | 5 GB storage | Frontend assets (if needed) |
| Firestore | 1 GB storage, 50K reads/day | User data, progress |
| Artifact Registry | 500 MB storage | Docker images |
| Cloud Build | 120 build-minutes/day | CI/CD |

**Key Principle**: Start simple, add complexity only when needed.

---

## Prerequisites

Before starting, you need:

1. **Google Account** - Your regular Gmail account works
2. **Credit/Debit Card** - Required for GCP signup (you won't be charged if you stay in free tier)
3. **Basic Terminal Knowledge** - Copy-paste commands into terminal

---

## Phase 1: GCP Account Setup (Day 1)

### Step 1.1: Create GCP Account

1. Go to https://cloud.google.com/
2. Click "Get started for free" or "Start free"
3. Sign in with your Google account
4. Enter your billing information (credit/debit card)
5. **Important**: New accounts get $300 free credits valid for 90 days!

### Step 1.2: Create a New Project

1. Go to https://console.cloud.google.com/
2. Click the project dropdown at the top (next to "Google Cloud")
3. Click "New Project"
4. Enter these details:
   - Project name: `cbse-learning-platform`
   - Organization: Leave as default
5. Click "Create"
6. Wait 30 seconds, then select your new project from the dropdown

### Step 1.3: Enable Required APIs

Open Cloud Shell (click the terminal icon `>_` at top right of GCP Console), then run:

```bash
# Enable required APIs (copy-paste this entire block)
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com
```

### Step 1.4: Set Up Budget Alert (CRITICAL!)

This prevents surprise bills:

1. Go to https://console.cloud.google.com/billing/budgets
2. Click "Create Budget"
3. Configure:
   - Budget name: `Monthly Budget`
   - Projects: Select `cbse-learning-platform`
   - Amount: `1000` INR (or `12` USD)
4. Set alerts at: 50%, 80%, 100%
5. Check "Email alerts to billing admins"
6. Click "Finish"

**You will now receive email alerts before exceeding your budget.**

---

## Phase 2: Prepare Your Code (Day 1-2)

### Step 2.1: Install Required Tools on Your Computer

**For Windows:**
1. Install Git: https://git-scm.com/download/win
2. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
3. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install

**For Mac:**
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install tools
brew install git
brew install --cask docker
brew install google-cloud-sdk
```

**For Linux (Ubuntu/Debian):**
```bash
# Install Git
sudo apt update && sudo apt install -y git

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2.2: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/sunkaramallikarjuna369/aitutorprompt.git
cd aitutorprompt
```

### Step 2.3: Authenticate with GCP

```bash
# Login to GCP (opens browser)
gcloud auth login

# Set your project
gcloud config set project cbse-learning-platform

# Configure Docker to use GCP
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

---

## Phase 3: Deploy Backend to Cloud Run (Day 2-3)

This is the main deployment step. We'll deploy a single Cloud Run service that serves both the backend API and frontend.

### Step 3.1: Create Artifact Registry Repository

```bash
# Create a repository to store Docker images
gcloud artifacts repositories create cbse-app \
  --repository-format=docker \
  --location=asia-south1 \
  --description="CBSE Learning Platform images"
```

### Step 3.2: Build the Frontend

```bash
# Navigate to frontend directory
cd cbse-learning-frontend

# Install dependencies
npm install

# Build for production (API URL will be same origin)
VITE_API_URL="" npm run build

# Copy built files to backend
cp -r dist ../cbse-learning-backend/

# Go back to root
cd ..
```

### Step 3.3: Build and Push Docker Image

```bash
# Navigate to backend
cd cbse-learning-backend

# Build the Docker image
docker build -t asia-south1-docker.pkg.dev/cbse-learning-platform/cbse-app/backend:v1 .

# Push to Artifact Registry
docker push asia-south1-docker.pkg.dev/cbse-learning-platform/cbse-app/backend:v1
```

### Step 3.4: Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/cbse-learning-platform/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="AI_PROVIDER=mock,APP_ENV=production"
```

### Step 3.5: Get Your App URL

After deployment, you'll see output like:
```
Service URL: https://cbse-learning-app-xxxxx-el.a.run.app
```

**Congratulations! Your app is now live!** Open this URL in your browser.

---

## Phase 4: Add Persistence with Firestore (Day 3-4)

Currently, the app uses in-memory storage (data resets on restart). Let's add Firestore for persistence.

### Step 4.1: Create Firestore Database

1. Go to https://console.cloud.google.com/firestore
2. Click "Create Database"
3. Select "Native mode" (recommended)
4. Choose location: `asia-south1` (Mumbai)
5. Click "Create Database"

### Step 4.2: Update Backend to Use Firestore

This requires code changes. For now, the in-memory database works fine for demos. We'll add Firestore integration in a future update.

---

## Phase 5: Set Up CI/CD with Cloud Build (Optional, Day 4-5)

Automate deployments when you push code changes.

### Step 5.1: Connect GitHub Repository

1. Go to https://console.cloud.google.com/cloud-build/triggers
2. Click "Connect Repository"
3. Select "GitHub" and authorize
4. Select your repository: `sunkaramallikarjuna369/aitutorprompt`
5. Click "Connect"

### Step 5.2: Create Build Trigger

1. Click "Create Trigger"
2. Configure:
   - Name: `deploy-on-push`
   - Event: Push to branch
   - Branch: `^main$`
   - Configuration: Cloud Build configuration file
   - Location: `/infra/cloudbuild/cloudbuild-simple.yaml`
3. Click "Create"

Now, every push to main will automatically deploy!

---

## Cost Breakdown

### Expected Monthly Costs (Low Traffic)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | ~10,000 requests | FREE (within free tier) |
| Artifact Registry | ~200 MB | FREE (within free tier) |
| Cloud Build | ~10 builds | FREE (within free tier) |
| Firestore | ~1,000 reads/day | FREE (within free tier) |
| **Total** | | **~0 INR** |

### What Will Increase Costs

| Action | Cost Impact |
|--------|-------------|
| Cloud Run min-instances > 0 | +$15-30/month |
| Cloud SQL (PostgreSQL) | +$10-50/month |
| Memorystore (Redis) | +$30-100/month |
| Vertex AI (Gemini) | +$5-50/month (per usage) |
| High traffic (>100K requests) | Variable |

---

## Troubleshooting

### "Permission Denied" Errors

```bash
# Re-authenticate
gcloud auth login
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

### "Quota Exceeded" Errors

1. Check your budget: https://console.cloud.google.com/billing/budgets
2. Check quotas: https://console.cloud.google.com/iam-admin/quotas
3. Wait for free tier to reset (monthly)

### Docker Build Fails

```bash
# Make sure Docker is running
docker info

# If on Linux, add yourself to docker group
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Cloud Run Deployment Fails

```bash
# Check logs
gcloud run services logs read cbse-learning-app --region=asia-south1

# Check service status
gcloud run services describe cbse-learning-app --region=asia-south1
```

---

## Incremental Upgrade Path

As your budget and needs grow, follow this path:

### Level 1: Free Tier (0-1000 INR/month) - CURRENT
- Single Cloud Run service
- In-memory database
- Mock AI provider
- Good for: Demos, testing, small classes

### Level 2: Basic Persistence (1000-3000 INR/month)
- Add Firestore for user data
- Add Cloud Storage for media
- Good for: Small school (50-100 students)

### Level 3: Production Ready (3000-10000 INR/month)
- Add Cloud SQL for relational data
- Add Memorystore for caching
- Enable Vertex AI for real AI features
- Good for: Medium school (100-500 students)

### Level 4: Scale (10000+ INR/month)
- Multiple Cloud Run services
- Load balancing with Cloud CDN
- Full monitoring and alerting
- Good for: Large institution (500+ students)

---

## Delete Everything (If Needed)

To avoid any charges, delete all resources:

```bash
# Delete Cloud Run service
gcloud run services delete cbse-learning-app --region=asia-south1 --quiet

# Delete Artifact Registry images
gcloud artifacts docker images delete \
  asia-south1-docker.pkg.dev/cbse-learning-platform/cbse-app/backend --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete cbse-app --location=asia-south1 --quiet

# Delete Firestore database (if created)
# Go to Console > Firestore > Delete database

# Delete the entire project (nuclear option)
gcloud projects delete cbse-learning-platform --quiet
```

---

## Quick Reference Commands

```bash
# View deployed services
gcloud run services list

# View service logs
gcloud run services logs read cbse-learning-app --region=asia-south1

# Update service with new image
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/cbse-learning-platform/cbse-app/backend:v2 \
  --region=asia-south1

# Check billing
gcloud billing accounts list

# Check project info
gcloud projects describe cbse-learning-platform
```

---

## PDF Ingestion Pipeline

The platform includes a PDF ingestion pipeline for processing NCERT textbooks and generating AI-driven visualizations.

### GCS Naming Strategy

PDFs and visualizations are organized using a hierarchical naming convention:

```
gs://your-bucket/
  cbse/
    class-10/
      mathematics/
        quadratic-equations/
          chapter.pdf                    # Source PDF
          visualizations/
            standard-form/
              dull.json                  # Visualization for Dull mode
              average.json               # Visualization for Average mode
              clever.json                # Visualization for Clever mode
            discriminant/
              dull.json
              average.json
              clever.json
    class-9/
      science/
        ...
```

This structure allows:
- Easy browsing by class level
- Organization by subject within each class
- Chapter-specific content grouping
- Cached visualizations stored alongside source PDFs

### PDF Ingestion Workflow

1. **Upload PDF** (via file upload or URL):
   ```bash
   # Upload a PDF file
   curl -X POST "https://your-app.run.app/pdf-ingestion/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@quadratic-equations.pdf" \
     -F "class_level=10" \
     -F "subject=Mathematics" \
     -F "chapter=Quadratic Equations"
   
   # Or download from NCERT URL
   curl -X POST "https://your-app.run.app/pdf-ingestion/from-url" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://ncert.nic.in/textbook/pdf/jemh104.pdf",
       "class_level": "10",
       "subject": "Mathematics",
       "chapter": "Quadratic Equations"
     }'
   ```

2. **Process PDF** (extract text and topics):
   ```bash
   curl -X POST "https://your-app.run.app/pdf-ingestion/process/{pdf_id}" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Generate Visualizations** (for each student mode):
   ```bash
   # Generate for a specific topic and mode
   curl -X POST "https://your-app.run.app/pdf-ingestion/generate-visualization" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "pdf_id": "abc123",
       "topic_name": "Standard Form",
       "student_mode": "dull"
     }'
   
   # Or batch generate all visualizations
   curl -X POST "https://your-app.run.app/pdf-ingestion/generate-all-visualizations/{pdf_id}" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Cost Optimization for PDF Pipeline

The PDF ingestion pipeline is designed to minimize AI costs:

1. **Caching**: All generated visualizations are cached. Subsequent requests return cached results without calling Gemini.

2. **Batch Processing**: Use `generate-all-visualizations` to pre-generate all visualizations once, then serve from cache.

3. **Mock Provider**: For development/testing, use `AI_PROVIDER=mock` to avoid any Gemini costs.

4. **GCS Storage**: In production, cached visualizations are stored in GCS for persistence across restarts.

### NCERT Textbook Sources

NCERT textbooks can be downloaded from: https://ncert.nic.in/textbook.php

Example workflow:
1. Visit the NCERT website
2. Select Class, Subject, and Chapter
3. Copy the PDF download link
4. Use the `/pdf-ingestion/from-url` endpoint with the link

---

## Next Steps

1. **Test Your Deployment**: Open the Cloud Run URL and try registering/logging in
2. **Share with Students**: Give them the URL to access the platform
3. **Monitor Usage**: Check Cloud Console for usage metrics
4. **Iterate**: Add features based on feedback
5. **Upload NCERT PDFs**: Use the PDF ingestion pipeline to add chapter content

---

## Getting Help

- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Run Guide**: https://cloud.google.com/run/docs
- **GCP Free Tier Details**: https://cloud.google.com/free
- **Community Support**: https://stackoverflow.com/questions/tagged/google-cloud-platform

---

*This guide was created for the CBSE Learning Platform project. Last updated: December 2024*
