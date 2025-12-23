# CBSE Learning Platform - Complete Step-by-Step Implementation Guide

This guide walks you through every single step to deploy the CBSE Learning Platform on Google Cloud Platform (GCP), starting from creating a Google account. No prior GCP experience required.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Create Google Account](#2-create-google-account)
3. [Create GCP Account](#3-create-gcp-account)
4. [Set Up Billing](#4-set-up-billing)
5. [Create GCP Project](#5-create-gcp-project)
6. [Set Budget Alerts](#6-set-budget-alerts)
7. [Install Required Tools](#7-install-required-tools)
8. [Clone the Repository](#8-clone-the-repository)
9. [Enable GCP APIs](#9-enable-gcp-apis)
10. [Create Artifact Registry](#10-create-artifact-registry)
11. [Build Docker Image](#11-build-docker-image)
12. [Push Image to Registry](#12-push-image-to-registry)
13. [Deploy to Cloud Run](#13-deploy-to-cloud-run)
14. [Test the Deployment](#14-test-the-deployment)
15. [Set Up Firebase Authentication](#15-set-up-firebase-authentication)
16. [Set Up Firestore Database](#16-set-up-firestore-database)
17. [Set Up Cloud Storage](#17-set-up-cloud-storage)
18. [Configure Vertex AI](#18-configure-vertex-ai)
19. [Set Up CI/CD](#19-set-up-cicd)
20. [Upload NCERT PDFs](#20-upload-ncert-pdfs)
21. [Monitor and Maintain](#21-monitor-and-maintain)
22. [Troubleshooting](#22-troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:

- A computer with internet access
- A valid phone number for verification
- A debit/credit card OR UPI (for Indian users) - required for GCP billing verification
- Basic familiarity with using a terminal/command prompt

**Time Required**: 2-4 hours for complete setup

**Budget**: 0-1000 INR/month (can run entirely on free tier)

---

## 2. Create Google Account

If you already have a Google account (Gmail), skip to [Step 3](#3-create-gcp-account).

### Step 2.1: Go to Google Account Creation Page

1. Open your web browser
2. Go to: https://accounts.google.com/signup
3. You will see the "Create your Google Account" page

### Step 2.2: Enter Your Information

1. **First name**: Enter your first name
2. **Last name**: Enter your last name
3. Click **Next**

### Step 2.3: Enter Basic Information

1. **Birthday**: Select your date of birth
2. **Gender**: Select your gender
3. Click **Next**

### Step 2.4: Choose Your Email Address

1. You can either:
   - Create a new Gmail address (recommended)
   - Use your existing email address
2. If creating new Gmail:
   - Enter your desired username (e.g., `yourname.cbse.learning`)
   - Gmail will suggest alternatives if your choice is taken
3. Click **Next**

### Step 2.5: Create Password

1. Enter a strong password (at least 8 characters)
2. Use a mix of letters, numbers, and symbols
3. Re-enter the password to confirm
4. Click **Next**

### Step 2.6: Add Recovery Phone (Recommended)

1. Enter your phone number
2. Click **Next**
3. You will receive an SMS with a verification code
4. Enter the code and click **Verify**

### Step 2.7: Add Recovery Email (Optional)

1. Enter an alternative email address for account recovery
2. Or click **Skip**

### Step 2.8: Review and Accept Terms

1. Review your account information
2. Click **Next**
3. Read Google's Terms of Service and Privacy Policy
4. Click **I agree**

**Your Google account is now created!**

---

## 3. Create GCP Account

### Step 3.1: Go to Google Cloud Console

1. Open your web browser
2. Go to: https://console.cloud.google.com/
3. Sign in with your Google account if not already signed in

### Step 3.2: Accept Terms of Service

1. You will see the Google Cloud Platform Terms of Service
2. Check the box: "I agree to the Google Cloud Platform Terms of Service"
3. Check the box for email updates (optional)
4. Select your country: **India**
5. Click **AGREE AND CONTINUE**

### Step 3.3: Welcome to Google Cloud

1. You will see the Google Cloud Console dashboard
2. A popup may appear offering a free trial - we'll set this up next

---

## 4. Set Up Billing

GCP requires a billing account even for free tier usage. You won't be charged unless you exceed free tier limits.

### Step 4.1: Start Free Trial

1. Look for the "Activate" or "Try for free" button in the top bar
2. Or go to: https://console.cloud.google.com/freetrial
3. Click **ACTIVATE** or **START FREE TRIAL**

### Step 4.2: Account Information (Step 1 of 2)

1. **Country**: Select **India**
2. **What best describes your organization**: Select **Personal project** or appropriate option
3. Check the box to agree to Terms of Service
4. Click **CONTINUE**

### Step 4.3: Payment Information (Step 2 of 2)

1. **Account type**: Select **Individual**
2. **Name and address**: Enter your details
   - Name: Your full name
   - Address line 1: Your street address
   - City: Your city
   - State: Your state
   - Postal code: Your PIN code
3. **Payment method**: 
   - For Indian users: You can use UPI, Debit Card, or Credit Card
   - Enter your card details or UPI ID
4. Click **START MY FREE TRIAL**

### Step 4.4: Verify Your Identity

1. Google may charge a small amount (usually ₹2) to verify your card
2. This amount will be refunded
3. Complete any additional verification steps

### Step 4.5: Free Trial Confirmation

1. You will see a confirmation message
2. You now have:
   - **$300 USD free credits** (approximately ₹25,000)
   - **90 days** to use these credits
   - After 90 days, you'll only be charged if you upgrade to a paid account

**Important**: The free trial will NOT automatically charge you. You must manually upgrade to continue after the trial.

---

## 5. Create GCP Project

### Step 5.1: Open Project Selector

1. In the Google Cloud Console, look at the top bar
2. Click on the project dropdown (it may say "Select a project" or show a project name)
3. A dialog will appear

### Step 5.2: Create New Project

1. Click **NEW PROJECT** in the top right of the dialog
2. Enter project details:
   - **Project name**: `cbse-learning-platform`
   - **Project ID**: Will be auto-generated (you can customize it)
   - **Location**: Leave as "No organization" for personal projects
3. Click **CREATE**

### Step 5.3: Wait for Project Creation

1. A notification will appear showing project creation progress
2. Wait for "Create Project: cbse-learning-platform" to complete
3. This usually takes 30-60 seconds

### Step 5.4: Select Your Project

1. Click on the notification or go to project selector
2. Select **cbse-learning-platform**
3. The console will now show your new project

### Step 5.5: Note Your Project ID

1. Go to: https://console.cloud.google.com/home/dashboard
2. Find "Project info" card
3. Note down your **Project ID** (e.g., `cbse-learning-platform-12345`)
4. You'll need this later

---

## 6. Set Budget Alerts

Protect yourself from unexpected charges by setting up budget alerts.

### Step 6.1: Go to Budgets Page

1. In the Cloud Console, click the hamburger menu (☰) in the top left
2. Scroll down and click **Billing**
3. Select your billing account
4. In the left sidebar, click **Budgets & alerts**

### Step 6.2: Create Budget

1. Click **CREATE BUDGET**
2. Enter budget details:
   - **Name**: `CBSE Learning Budget`
   - **Time range**: Monthly
   - **Projects**: Select `cbse-learning-platform`
3. Click **NEXT**

### Step 6.3: Set Budget Amount

1. **Budget type**: Select **Specified amount**
2. **Target amount**: Enter `1000` (for ₹1000/month)
   - Note: GCP shows amounts in your billing currency
3. Click **NEXT**

### Step 6.4: Set Alert Thresholds

1. Default thresholds are set at 50%, 90%, and 100%
2. Add additional threshold:
   - Click **ADD THRESHOLD**
   - Enter `80` for 80%
3. **Manage notifications**:
   - Check **Email alerts to billing admins and users**
   - Optionally add additional email addresses
4. Click **FINISH**

### Step 6.5: Verify Budget Created

1. You should see your budget in the list
2. Current spend should show ₹0.00

---

## 7. Install Required Tools

You need to install some tools on your computer to deploy the application.

### Step 7.1: Install Google Cloud SDK (gcloud CLI)

#### For Windows:

1. Download the installer from: https://cloud.google.com/sdk/docs/install
2. Run the downloaded `GoogleCloudSDKInstaller.exe`
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation location (default is fine)
   - Select components (default is fine)
4. Check "Run 'gcloud init'" at the end
5. Click **Install**

#### For macOS:

1. Open Terminal
2. Run:
   ```bash
   curl https://sdk.cloud.google.com | bash
   ```
3. Restart your terminal
4. Run:
   ```bash
   gcloud init
   ```

#### For Linux (Ubuntu/Debian):

1. Open Terminal
2. Run:
   ```bash
   sudo apt-get update
   sudo apt-get install apt-transport-https ca-certificates gnupg curl
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   sudo apt-get update && sudo apt-get install google-cloud-cli
   ```

### Step 7.2: Initialize gcloud

1. Open Terminal (or Command Prompt on Windows)
2. Run:
   ```bash
   gcloud init
   ```
3. When prompted:
   - **Would you like to log in?**: Enter `Y`
   - A browser window will open
   - Sign in with your Google account
   - Click **Allow** to grant permissions
4. Back in terminal:
   - **Pick cloud project**: Select `cbse-learning-platform`
   - **Configure default region**: Enter the number for `asia-south1` (Mumbai)

### Step 7.3: Verify gcloud Installation

Run:
```bash
gcloud config list
```

You should see output like:
```
[core]
account = your-email@gmail.com
project = cbse-learning-platform

[compute]
region = asia-south1
```

### Step 7.4: Install Docker

#### For Windows:

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Follow the installation wizard
4. Restart your computer when prompted
5. Start Docker Desktop from the Start menu
6. Wait for Docker to start (whale icon in system tray)

#### For macOS:

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Open the downloaded `.dmg` file
3. Drag Docker to Applications folder
4. Open Docker from Applications
5. Wait for Docker to start

#### For Linux (Ubuntu):

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

### Step 7.5: Verify Docker Installation

Run:
```bash
docker --version
```

You should see output like:
```
Docker version 24.0.0, build ...
```

### Step 7.6: Install Git

#### For Windows:

1. Download Git from: https://git-scm.com/download/win
2. Run the installer
3. Use default options throughout
4. Click **Install**

#### For macOS:

```bash
# Git is usually pre-installed. If not:
xcode-select --install
```

#### For Linux:

```bash
sudo apt-get install git
```

### Step 7.7: Verify Git Installation

Run:
```bash
git --version
```

You should see output like:
```
git version 2.40.0
```

---

## 8. Clone the Repository

### Step 8.1: Create Working Directory

```bash
# Create a directory for the project
mkdir -p ~/projects
cd ~/projects
```

### Step 8.2: Clone the Repository

```bash
git clone https://github.com/sunkaramallikarjuna369/aitutorprompt.git
cd aitutorprompt
```

### Step 8.3: Switch to the Correct Branch

```bash
git checkout devin/1766473437-low-budget-gcp-guide
```

### Step 8.4: Verify Repository Contents

```bash
ls -la
```

You should see:
```
cbse-learning-backend/
cbse-learning-frontend/
docs/
infra/
README.md
```

---

## 9. Enable GCP APIs

You need to enable several APIs for the services we'll use.

### Step 9.1: Enable APIs via gcloud

Run each command one by one:

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Firestore API
gcloud services enable firestore.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Vertex AI API (for AI features)
gcloud services enable aiplatform.googleapis.com

# Enable Secret Manager API (for storing secrets)
gcloud services enable secretmanager.googleapis.com

# Enable Identity Platform API (for Firebase Auth)
gcloud services enable identitytoolkit.googleapis.com
```

### Step 9.2: Verify APIs are Enabled

```bash
gcloud services list --enabled
```

You should see all the APIs listed above in the output.

---

## 10. Create Artifact Registry

Artifact Registry stores your Docker images.

### Step 10.1: Create Repository

```bash
gcloud artifacts repositories create cbse-app \
  --repository-format=docker \
  --location=asia-south1 \
  --description="CBSE Learning Platform Docker images"
```

### Step 10.2: Configure Docker Authentication

```bash
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

When prompted, enter `Y` to confirm.

### Step 10.3: Verify Repository Created

```bash
gcloud artifacts repositories list --location=asia-south1
```

You should see:
```
REPOSITORY  FORMAT  DESCRIPTION
cbse-app    DOCKER  CBSE Learning Platform Docker images
```

---

## 11. Build Docker Image

### Step 11.1: Navigate to Backend Directory

```bash
cd ~/projects/aitutorprompt/cbse-learning-backend
```

### Step 11.2: Review Dockerfile

```bash
cat Dockerfile
```

The Dockerfile should already be configured for the application.

### Step 11.3: Build the Docker Image

```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID=$(gcloud config get-value project)

# Build the image
docker build -t asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 .
```

This will take 5-10 minutes on first build.

### Step 11.4: Verify Image Built

```bash
docker images | grep cbse-app
```

You should see your image listed.

---

## 12. Push Image to Registry

### Step 12.1: Push the Image

```bash
docker push asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1
```

This will take a few minutes depending on your internet speed.

### Step 12.2: Verify Image in Registry

```bash
gcloud artifacts docker images list asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app
```

You should see your image listed.

---

## 13. Deploy to Cloud Run

### Step 13.1: Deploy the Application

```bash
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="AI_PROVIDER=mock,APP_ENV=production"
```

### Step 13.2: Wait for Deployment

The deployment will take 1-2 minutes. You'll see progress messages.

### Step 13.3: Get Your Application URL

After deployment, you'll see output like:
```
Service [cbse-learning-app] revision [cbse-learning-app-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://cbse-learning-app-xxxxx-el.a.run.app
```

**Copy this URL** - this is your live application!

### Step 13.4: Save the URL

```bash
# Save the URL for later use
export APP_URL=$(gcloud run services describe cbse-learning-app --region=asia-south1 --format='value(status.url)')
echo "Your app URL: $APP_URL"
```

---

## 14. Test the Deployment

### Step 14.1: Test API Root

```bash
curl $APP_URL/
```

You should see a JSON response with available services.

### Step 14.2: Test Health Endpoint

```bash
curl $APP_URL/health
```

You should see:
```json
{"status": "healthy"}
```

### Step 14.3: Open in Browser

1. Copy your application URL
2. Open it in a web browser
3. You should see the CBSE Learning Platform login page

### Step 14.4: Test Login

1. Use test credentials:
   - Username: `user`
   - Password: `dd058af30a635609e894c13b4e524841`
2. Click Login
3. You should see the dashboard

### Step 14.5: Test API Documentation

1. Go to: `https://your-app-url/docs`
2. You should see the Swagger API documentation
3. You can test endpoints directly from this page

---

## 15. Set Up Firebase Authentication

Firebase provides free authentication for up to 50,000 monthly active users.

### Step 15.1: Go to Firebase Console

1. Open: https://console.firebase.google.com/
2. Sign in with your Google account

### Step 15.2: Add Firebase to Your Project

1. Click **Add project** (or **Create a project**)
2. Enter project name: `cbse-learning-platform`
3. **Important**: Click **Add Firebase to a Google Cloud project**
4. Select your existing GCP project: `cbse-learning-platform`
5. Click **Continue**

### Step 15.3: Configure Google Analytics (Optional)

1. You can disable Google Analytics to simplify setup
2. Toggle off **Enable Google Analytics for this project**
3. Click **Add Firebase**

### Step 15.4: Wait for Setup

1. Firebase will configure your project
2. This takes about 1 minute
3. Click **Continue** when done

### Step 15.5: Enable Authentication

1. In Firebase Console, click **Build** in the left sidebar
2. Click **Authentication**
3. Click **Get started**

### Step 15.6: Enable Email/Password Sign-in

1. Go to **Sign-in method** tab
2. Click **Email/Password**
3. Toggle **Enable** to ON
4. Click **Save**

### Step 15.7: Enable Google Sign-in (Optional)

1. Click **Add new provider**
2. Click **Google**
3. Toggle **Enable** to ON
4. Enter your email as **Project support email**
5. Click **Save**

### Step 15.8: Download Service Account Key

1. Click the gear icon (⚙️) next to **Project Overview**
2. Click **Project settings**
3. Go to **Service accounts** tab
4. Click **Generate new private key**
5. Click **Generate key**
6. Save the downloaded JSON file securely (e.g., `firebase-credentials.json`)

**IMPORTANT**: Never commit this file to git or share it publicly!

### Step 15.9: Upload Credentials to Secret Manager

```bash
# Create secret from the downloaded file
gcloud secrets create firebase-credentials \
  --data-file=/path/to/your/firebase-credentials.json

# Get your project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 15.10: Update Cloud Run with Firebase

```bash
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="AI_PROVIDER=mock,APP_ENV=production" \
  --set-secrets="FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest"
```

---

## 16. Set Up Firestore Database

Firestore provides a NoSQL database with a generous free tier.

### Step 16.1: Go to Firestore Console

1. Go to: https://console.cloud.google.com/firestore
2. Make sure your project is selected

### Step 16.2: Create Database

1. Click **Create Database**
2. Select **Native mode** (recommended for new projects)
3. Click **Continue**

### Step 16.3: Choose Location

1. Select **asia-south1 (Mumbai)** for lowest latency in India
2. Click **Create Database**

### Step 16.4: Wait for Creation

1. Database creation takes 1-2 minutes
2. You'll see the Firestore data browser when done

### Step 16.5: Verify Database

1. You should see an empty database
2. Collections will be created automatically when the app writes data

---

## 17. Set Up Cloud Storage

Cloud Storage is used for storing PDFs and generated visualizations.

### Step 17.1: Go to Cloud Storage Console

1. Go to: https://console.cloud.google.com/storage
2. Make sure your project is selected

### Step 17.2: Create Bucket

1. Click **CREATE BUCKET**
2. Enter bucket name: `cbse-learning-platform-storage` (must be globally unique)
   - If taken, try: `cbse-learning-platform-storage-[your-initials]`
3. Click **Continue**

### Step 17.3: Choose Location

1. Select **Region**
2. Choose **asia-south1 (Mumbai)**
3. Click **Continue**

### Step 17.4: Choose Storage Class

1. Select **Standard** (best for frequently accessed data)
2. Click **Continue**

### Step 17.5: Access Control

1. Select **Uniform** (recommended)
2. Uncheck **Enforce public access prevention** if you want public access to some files
3. Click **Continue**

### Step 17.6: Protection Tools

1. Leave defaults (no additional protection needed for MVP)
2. Click **CREATE**

### Step 17.7: Create Folder Structure

1. Click on your bucket name
2. Click **CREATE FOLDER**
3. Create these folders:
   - `cbse/class-10/mathematics/quadratic-equations`
4. This follows the GCS naming strategy for organizing content

### Step 17.8: Update Cloud Run with Storage Bucket

```bash
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="AI_PROVIDER=mock,APP_ENV=production,GCS_BUCKET=cbse-learning-platform-storage" \
  --set-secrets="FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest"
```

---

## 18. Configure Vertex AI

Vertex AI provides AI capabilities using Google's Gemini model.

### Step 18.1: Enable Vertex AI

```bash
gcloud services enable aiplatform.googleapis.com
```

### Step 18.2: Grant Permissions

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Vertex AI User role to Cloud Run service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Step 18.3: Update Cloud Run to Use Vertex AI

```bash
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="AI_PROVIDER=vertex,APP_ENV=production,GCS_BUCKET=cbse-learning-platform-storage,VERTEX_AI_PROJECT=$PROJECT_ID,VERTEX_AI_LOCATION=asia-south1" \
  --set-secrets="FIREBASE_CREDENTIALS_PATH=firebase-credentials:latest"
```

**Note**: Using `AI_PROVIDER=vertex` will incur costs. For free operation, use `AI_PROVIDER=mock`.

### Step 18.4: Test Vertex AI (Optional)

```bash
curl -X POST "$APP_URL/visualization-orchestrator/topics/topic-1/config" \
  -H "Content-Type: application/json" \
  -d '{"student_mode": "average"}'
```

---

## 19. Set Up CI/CD

Automate deployments when you push code changes.

### Step 19.1: Go to Cloud Build Console

1. Go to: https://console.cloud.google.com/cloud-build
2. Make sure your project is selected

### Step 19.2: Connect GitHub Repository

1. Click **Triggers** in the left sidebar
2. Click **CONNECT REPOSITORY**
3. Select **GitHub (Cloud Build GitHub App)**
4. Click **Continue**

### Step 19.3: Authenticate with GitHub

1. Click **Authenticate**
2. Sign in to GitHub if prompted
3. Click **Authorize Google Cloud Build**

### Step 19.4: Select Repository

1. Select your GitHub account
2. Find and select `aitutorprompt` repository
3. Check the consent checkbox
4. Click **Connect**

### Step 19.5: Create Build Trigger

1. Click **CREATE TRIGGER**
2. Configure trigger:
   - **Name**: `deploy-on-push`
   - **Description**: `Deploy to Cloud Run on push to main`
   - **Event**: Push to a branch
   - **Source**: 
     - Repository: `sunkaramallikarjuna369/aitutorprompt`
     - Branch: `^main$` (or `^devin/1766473437-low-budget-gcp-guide$` for this branch)
   - **Configuration**: Cloud Build configuration file
   - **Location**: `/infra/cloudbuild/cloudbuild-simple.yaml`
3. Click **CREATE**

### Step 19.6: Grant Cloud Build Permissions

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Service Account User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### Step 19.7: Test CI/CD

1. Make a small change to any file in the repository
2. Commit and push to the configured branch
3. Go to Cloud Build > History to see the build running
4. Wait for the build to complete (5-10 minutes)
5. Your app will be automatically updated

---

## 20. Upload NCERT PDFs

Now let's add actual CBSE content to the platform.

### Step 20.1: Download NCERT PDF

1. Go to: https://ncert.nic.in/textbook.php
2. Select:
   - Class: **X**
   - Subject: **Mathematics**
   - Book: **Mathematics**
3. Find Chapter 4: **Quadratic Equations**
4. Click the PDF icon to download

### Step 20.2: Upload PDF via API

```bash
# Upload the PDF
curl -X POST "$APP_URL/pdf-ingestion/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/quadratic-equations.pdf" \
  -F "class_level=10" \
  -F "subject=Mathematics" \
  -F "chapter=Quadratic Equations"
```

To get a JWT token, first login:
```bash
# Login to get token
TOKEN=$(curl -s -X POST "$APP_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "dd058af30a635609e894c13b4e524841"}' | jq -r '.access_token')

echo "Your token: $TOKEN"
```

### Step 20.3: Process the PDF

```bash
# Get the PDF ID from the upload response, then process it
curl -X POST "$APP_URL/pdf-ingestion/process/YOUR_PDF_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 20.4: Generate Visualizations

```bash
# Generate all visualizations for all student modes
curl -X POST "$APP_URL/pdf-ingestion/generate-all-visualizations/YOUR_PDF_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 20.5: Index for RAG

```bash
# Index the PDF for question answering
curl -X POST "$APP_URL/rag-agent/index/YOUR_PDF_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 20.6: Test RAG Agent

```bash
# Ask a question about the PDF
curl -X POST "$APP_URL/rag-agent/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_id": "YOUR_PDF_ID",
    "question": "What is the quadratic formula?",
    "student_mode": "average",
    "include_visualization": true
  }'
```

---

## 21. Monitor and Maintain

### Step 21.1: View Application Logs

```bash
gcloud run services logs read cbse-learning-app --region=asia-south1 --limit=100
```

### Step 21.2: Monitor in Console

1. Go to: https://console.cloud.google.com/run
2. Click on `cbse-learning-app`
3. View:
   - **Metrics**: Request count, latency, errors
   - **Logs**: Application logs
   - **Revisions**: Deployment history

### Step 21.3: Set Up Alerts (Optional)

1. Go to: https://console.cloud.google.com/monitoring/alerting
2. Click **CREATE POLICY**
3. Configure alert for:
   - High error rate
   - High latency
   - Budget threshold exceeded

### Step 21.4: Check Billing

1. Go to: https://console.cloud.google.com/billing
2. View current charges
3. Check budget status

### Step 21.5: Scale as Needed

To handle more traffic:
```bash
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v1 \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=2 \
  --min-instances=1 \
  --max-instances=10 \
  --set-env-vars="AI_PROVIDER=vertex,APP_ENV=production"
```

---

## 22. Troubleshooting

### Problem: "Permission Denied" Errors

**Solution**:
```bash
# Re-authenticate
gcloud auth login
gcloud auth configure-docker asia-south1-docker.pkg.dev

# Verify project
gcloud config set project cbse-learning-platform
```

### Problem: Docker Build Fails

**Solution**:
```bash
# Make sure Docker is running
docker info

# If on Linux, ensure you're in docker group
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Problem: Cloud Run Deployment Fails

**Solution**:
```bash
# Check logs
gcloud run services logs read cbse-learning-app --region=asia-south1

# Check service status
gcloud run services describe cbse-learning-app --region=asia-south1
```

### Problem: API Returns 500 Error

**Solution**:
1. Check application logs:
   ```bash
   gcloud run services logs read cbse-learning-app --region=asia-south1 --limit=50
   ```
2. Verify environment variables are set correctly
3. Check if required APIs are enabled

### Problem: Firebase Authentication Not Working

**Solution**:
1. Verify Firebase credentials are uploaded to Secret Manager
2. Check that Cloud Run has access to the secret
3. Verify Firebase project is linked to GCP project

### Problem: Vertex AI Returns Errors

**Solution**:
1. Verify Vertex AI API is enabled
2. Check service account has `aiplatform.user` role
3. Try using `AI_PROVIDER=mock` to test without AI

### Problem: Budget Exceeded

**Solution**:
1. Set `min-instances=0` to scale to zero when idle
2. Use `AI_PROVIDER=mock` instead of Vertex AI
3. Delete unused resources:
   ```bash
   # Delete Cloud Run service
   gcloud run services delete cbse-learning-app --region=asia-south1
   ```

### Problem: Slow Response Times

**Solution**:
1. Increase memory/CPU:
   ```bash
   gcloud run deploy cbse-learning-app --memory=1Gi --cpu=2
   ```
2. Set `min-instances=1` to avoid cold starts (increases cost)

---

## Quick Reference Commands

```bash
# View deployed services
gcloud run services list

# View service logs
gcloud run services logs read cbse-learning-app --region=asia-south1

# Update service with new image
gcloud run deploy cbse-learning-app \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend:v2 \
  --region=asia-south1

# Check billing
gcloud billing accounts list

# Check project info
gcloud projects describe $PROJECT_ID

# Delete everything (if needed)
gcloud run services delete cbse-learning-app --region=asia-south1 --quiet
gcloud artifacts docker images delete asia-south1-docker.pkg.dev/$PROJECT_ID/cbse-app/backend --quiet
gcloud artifacts repositories delete cbse-app --location=asia-south1 --quiet
```

---

## Summary

You have now:

1. Created a Google account
2. Set up GCP with free trial credits
3. Created a project with budget alerts
4. Installed all required tools
5. Deployed the CBSE Learning Platform to Cloud Run
6. Set up Firebase Authentication
7. Configured Firestore database
8. Set up Cloud Storage for PDFs
9. Configured Vertex AI for AI features
10. Set up CI/CD for automatic deployments
11. Uploaded NCERT content
12. Learned how to monitor and maintain the application

**Your application is now live and ready for students to use!**

---

## Next Steps

1. **Share with students**: Give them the Cloud Run URL
2. **Upload more content**: Add more chapters and subjects
3. **Customize**: Modify the frontend for your school's branding
4. **Scale**: Increase resources as usage grows
5. **Feedback**: Collect student feedback and iterate

---

## Getting Help

- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Run Guide**: https://cloud.google.com/run/docs
- **Firebase Docs**: https://firebase.google.com/docs
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/google-cloud-platform

---

*This guide was created for the CBSE Learning Platform project. Last updated: December 2024*
