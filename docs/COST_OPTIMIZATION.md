# Cost Optimization Guide for GCP

This guide helps you minimize costs while running the CBSE Learning Platform on Google Cloud Platform.

## GCP Free Tier Summary

Google Cloud offers a generous free tier that resets monthly:

| Service | Free Allowance | Notes |
|---------|----------------|-------|
| **Cloud Run** | 2M requests/month, 360K GB-seconds, 180K vCPU-seconds | Scales to zero when idle |
| **Cloud Storage** | 5 GB-months, 5K Class A ops, 50K Class B ops | Standard storage in US regions |
| **Firestore** | 1 GB storage, 50K reads/day, 20K writes/day, 20K deletes/day | Native mode |
| **Artifact Registry** | 500 MB storage | Docker images |
| **Cloud Build** | 120 build-minutes/day | First 120 min free |
| **Cloud Logging** | 50 GB/month | First 50 GB free |

## Cost Killers to Avoid

These services will quickly exceed a 1000 INR budget:

### 1. Cloud SQL (PostgreSQL/MySQL)
- **Minimum cost**: ~$10-15/month for smallest instance
- **Alternative**: Use Firestore (free tier) or in-memory storage for MVP
- **When to use**: Only when you have 500+ active users and need complex queries

### 2. Memorystore (Redis)
- **Minimum cost**: ~$30/month for smallest instance
- **Alternative**: Use in-memory caching in Cloud Run (resets on cold start)
- **When to use**: Only when you have high traffic and need session persistence

### 3. Cloud Run with min-instances > 0
- **Cost impact**: ~$15-30/month per always-on instance
- **Solution**: Keep `min-instances=0` (scales to zero when idle)
- **Trade-off**: First request after idle period takes 2-5 seconds (cold start)

### 4. Vertex AI (Gemini)
- **Cost**: ~$0.0005-0.002 per 1K characters
- **Solution**: Use `AI_PROVIDER=mock` for development/demos
- **When to use**: Only in production with paying users

### 5. Cloud CDN
- **Cost**: ~$0.02-0.08 per GB egress
- **Solution**: Skip CDN for low traffic; serve from Cloud Run directly
- **When to use**: Only when you have 10K+ daily users

### 6. Cloud Logging (excessive)
- **Cost**: $0.50 per GB after 50 GB free
- **Solution**: Set log level to WARNING in production
- **How**: Add `--set-env-vars=LOG_LEVEL=WARNING` to Cloud Run deploy

## Cost-Saving Configurations

### Cloud Run Settings

```bash
gcloud run deploy cbse-learning-app \
  --memory=512Mi \           # Minimum needed (not 1Gi or 2Gi)
  --cpu=1 \                  # Single CPU is enough
  --min-instances=0 \        # Scale to zero when idle
  --max-instances=2 \        # Limit maximum scale
  --concurrency=80 \         # Handle 80 requests per instance
  --timeout=60 \             # 60 second timeout
  --cpu-throttling \         # Throttle CPU when not processing requests
  --region=asia-south1       # Mumbai region (closest to India)
```

### Environment Variables for Cost Savings

```bash
--set-env-vars="\
AI_PROVIDER=mock,\           # Don't use paid AI
LOG_LEVEL=WARNING,\          # Reduce logging
APP_ENV=production"
```

## Monthly Budget Tracking

### Set Up Budget Alerts

1. Go to: https://console.cloud.google.com/billing/budgets
2. Create budget with these thresholds:
   - 50% (500 INR) - Early warning
   - 80% (800 INR) - Take action
   - 100% (1000 INR) - Stop non-essential services

### Monitor Costs Daily

```bash
# View current month's costs
gcloud billing accounts list
# Then go to: https://console.cloud.google.com/billing
```

### Quick Cost Check Commands

```bash
# List all Cloud Run services and their status
gcloud run services list

# Check service configuration
gcloud run services describe cbse-learning-app --region=asia-south1

# View recent logs (check for errors causing retries)
gcloud run services logs read cbse-learning-app --region=asia-south1 --limit=50
```

## Cost Comparison: Different Architectures

### Option A: Single Cloud Run (Recommended for 1000 INR)

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Run (scales to zero) | FREE |
| Artifact Registry | FREE |
| Cloud Build (10 builds) | FREE |
| **Total** | **~0 INR** |

### Option B: Cloud Run + Firestore

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Run | FREE |
| Firestore (within free tier) | FREE |
| Artifact Registry | FREE |
| **Total** | **~0 INR** |

### Option C: Full Production (NOT for 1000 INR budget)

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Run (min-instances=1) | ~1500 INR |
| Cloud SQL (db-f1-micro) | ~1000 INR |
| Memorystore (1GB) | ~2500 INR |
| Cloud Storage + CDN | ~200 INR |
| Vertex AI | ~500 INR |
| **Total** | **~5700 INR** |

## Scaling Strategy

### Phase 1: Free Tier (0-100 users)
- Single Cloud Run service
- In-memory or Firestore storage
- Mock AI provider
- No CDN

### Phase 2: Basic Production (100-500 users, ~2000 INR/month)
- Cloud Run with min-instances=1 (faster response)
- Firestore for persistence
- Cloud Storage for media
- Still mock AI

### Phase 3: Full Production (500+ users, ~5000+ INR/month)
- Multiple Cloud Run services
- Cloud SQL for relational data
- Memorystore for caching
- Vertex AI for real AI features
- Cloud CDN for static assets

## Emergency Cost Reduction

If you're approaching budget limit:

```bash
# 1. Scale down Cloud Run
gcloud run services update cbse-learning-app \
  --min-instances=0 \
  --max-instances=1 \
  --region=asia-south1

# 2. Delete old Docker images
gcloud artifacts docker images list \
  asia-south1-docker.pkg.dev/PROJECT_ID/cbse-app/backend \
  --include-tags

# Delete old versions (keep only latest)
gcloud artifacts docker images delete \
  asia-south1-docker.pkg.dev/PROJECT_ID/cbse-app/backend:OLD_TAG

# 3. Disable Cloud Build triggers temporarily
gcloud builds triggers list
gcloud builds triggers update TRIGGER_NAME --disabled

# 4. Nuclear option: Delete everything
gcloud run services delete cbse-learning-app --region=asia-south1 --quiet
```

## Tips for Indian Users

1. **Use asia-south1 (Mumbai) region** - Lowest latency for Indian users
2. **Billing in INR** - GCP bills in USD but shows INR equivalent
3. **UPI payments** - Add UPI as payment method for easier billing
4. **Free credits** - New accounts get $300 (~25,000 INR) free credits for 90 days
5. **Student credits** - If you're a student, apply for Google Cloud for Students

## Monitoring Dashboard

Create a simple monitoring dashboard:

1. Go to: https://console.cloud.google.com/monitoring/dashboards
2. Create dashboard with these widgets:
   - Cloud Run request count
   - Cloud Run latency (p50, p95)
   - Cloud Run instance count
   - Billing: Current month spend

## Summary

For a 1000 INR/month budget:

1. Use **single Cloud Run service** with `min-instances=0`
2. Use **Firestore** instead of Cloud SQL
3. Use **mock AI provider** instead of Vertex AI
4. Skip **Memorystore** and **Cloud CDN**
5. Set up **budget alerts** immediately
6. Monitor costs **weekly**

This configuration can run entirely within GCP's free tier for low-traffic applications!
