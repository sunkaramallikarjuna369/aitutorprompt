# CBSE Learning Platform - Implementation Guide

This guide provides step-by-step instructions for implementing and deploying the CBSE Learning Platform on Google Cloud Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [GCP Project Setup](#gcp-project-setup)
4. [Infrastructure Deployment](#infrastructure-deployment)
5. [Application Deployment](#application-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required Tools

- Python 3.11+ with Poetry package manager
- Node.js 18+ with npm
- Google Cloud SDK (gcloud CLI)
- Terraform 1.0+
- Docker (for local container testing)
- Git

### Required Accounts

- Google Cloud Platform account with billing enabled
- GitHub account (for CI/CD integration)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sunkaramallikarjuna369/aitutorprompt.git
cd aitutorprompt
```

### 2. Backend Setup

```bash
cd cbse-learning-backend

# Install dependencies
poetry install

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run development server
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd cbse-learning-frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## GCP Project Setup

### 1. Create GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create project
gcloud projects create $PROJECT_ID --name="CBSE Learning Platform"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (required for most services)
# Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  firestore.googleapis.com \
  redis.googleapis.com \
  pubsub.googleapis.com \
  aiplatform.googleapis.com \
  identitytoolkit.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create cbse-learning-run \
  --display-name="CBSE Learning Platform Service Account"

# Grant required roles
for role in cloudsql.client datastore.user pubsub.publisher secretmanager.secretAccessor aiplatform.user storage.objectViewer; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cbse-learning-run@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/$role"
done
```

## Infrastructure Deployment

### Using Terraform

```bash
cd infra/terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# - project_id: Your GCP project ID
# - region: Preferred region (e.g., us-central1)
# - db_password: Secure database password
# - jwt_secret_key: Secure JWT signing key (32+ characters)

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply
```

### Manual Setup (Alternative)

If you prefer manual setup or need more control:

#### Cloud SQL

```bash
gcloud sql instances create cbse-learning-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

gcloud sql databases create cbse_learning \
  --instance=cbse-learning-db

gcloud sql users create cbse_app \
  --instance=cbse-learning-db \
  --password=YOUR_SECURE_PASSWORD
```

#### Firestore

```bash
gcloud firestore databases create \
  --location=us-central \
  --type=firestore-native
```

#### Redis

```bash
gcloud redis instances create cbse-learning-cache \
  --size=1 \
  --region=us-central1 \
  --tier=basic
```

#### Pub/Sub Topics

```bash
for topic in quiz-submitted lesson-viewed progress-updated; do
  gcloud pubsub topics create $topic
done
```

## Application Deployment

### Backend Deployment

#### Build and Push Docker Image

```bash
cd cbse-learning-backend

# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build image
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/cbse-learning/backend:latest .

# Push image
docker push us-central1-docker.pkg.dev/$PROJECT_ID/cbse-learning/backend:latest
```

#### Deploy to Cloud Run

```bash
gcloud run deploy cbse-learning-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/cbse-learning/backend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="AI_PROVIDER=vertex,VERTEX_AI_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=us-central1" \
  --service-account=cbse-learning-run@$PROJECT_ID.iam.gserviceaccount.com
```

### Frontend Deployment

#### Build Frontend

```bash
cd cbse-learning-frontend

# Get backend URL
BACKEND_URL=$(gcloud run services describe cbse-learning-backend --region=us-central1 --format='value(status.url)')

# Update environment
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Build
npm run build
```

#### Deploy to Cloud Storage

```bash
# Create bucket
gsutil mb -l us-central1 gs://$PROJECT_ID-cbse-frontend

# Enable website hosting
gsutil web set -m index.html -e index.html gs://$PROJECT_ID-cbse-frontend

# Upload files
gsutil -m rsync -r -d dist/ gs://$PROJECT_ID-cbse-frontend/

# Make public
gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-cbse-frontend
```

### CI/CD with Cloud Build

```bash
# Submit build
gcloud builds submit --config=infra/cloudbuild/cloudbuild.yaml

# Or set up trigger for automatic builds
gcloud builds triggers create github \
  --repo-name=aitutorprompt \
  --repo-owner=sunkaramallikarjuna369 \
  --branch-pattern="^main$" \
  --build-config=infra/cloudbuild/cloudbuild.yaml
```

## Post-Deployment Configuration

### 1. Configure Secrets

```bash
# Create JWT secret
echo -n "your-secure-jwt-secret-key" | \
  gcloud secrets create jwt-secret-key --data-file=-

# Create database password secret
echo -n "your-database-password" | \
  gcloud secrets create db-password --data-file=-
```

### 2. Configure Identity Platform

1. Go to [Identity Platform Console](https://console.cloud.google.com/customer-identity)
2. Enable Email/Password authentication
3. (Optional) Enable Google Sign-In
4. Configure authorized domains

### 3. Seed Initial Data

The platform includes seed data for Class 10 Mathematics - Quadratic Equations. For production, you may want to:

1. Export seed data to Firestore
2. Import question bank to Cloud SQL
3. Upload media assets to Cloud Storage

## Monitoring and Maintenance

### View Logs

```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cbse-learning-backend" --limit=50

# Or use Cloud Console
# https://console.cloud.google.com/logs
```

### Set Up Alerts

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
```

### Scaling Configuration

Cloud Run automatically scales based on traffic. To adjust:

```bash
gcloud run services update cbse-learning-backend \
  --min-instances=1 \
  --max-instances=10 \
  --concurrency=80
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend CORS configuration includes your frontend domain
2. **Database Connection**: Verify Cloud SQL connection string and IAM permissions
3. **Vertex AI Errors**: Check that the AI Platform API is enabled and service account has `aiplatform.user` role
4. **Build Failures**: Review Cloud Build logs for specific errors

### Getting Help

- Check the [README.md](../README.md) for general documentation
- Review [GCP Cloud Run documentation](https://cloud.google.com/run/docs)
- Open an issue on GitHub for platform-specific problems
