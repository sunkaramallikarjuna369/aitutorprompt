# CBSE Learning Platform - GCP Budget Estimate

This document provides cost estimates for running the CBSE Learning Platform on Google Cloud Platform at various scales.

## Cost Summary

| Environment | Monthly Cost (USD) | Annual Cost (USD) |
|-------------|-------------------|-------------------|
| Development/Testing | $50 - $100 | $600 - $1,200 |
| Small School (100 students) | $150 - $250 | $1,800 - $3,000 |
| Medium School (500 students) | $400 - $600 | $4,800 - $7,200 |
| Large Institution (2000+ students) | $1,000 - $2,000 | $12,000 - $24,000 |

## Detailed Cost Breakdown

### 1. Compute - Cloud Run

Cloud Run charges based on CPU, memory, and request count.

| Tier | vCPU | Memory | Requests/month | Est. Cost/month |
|------|------|--------|----------------|-----------------|
| Dev | 1 | 512 MB | 100K | $5 - $10 |
| Small | 2 | 1 GB | 1M | $30 - $50 |
| Medium | 2 | 2 GB | 5M | $100 - $150 |
| Large | 4 | 4 GB | 20M | $300 - $500 |

**Pricing Details:**
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests
- Free tier: 2 million requests/month, 360,000 GiB-seconds, 180,000 vCPU-seconds

### 2. Database - Cloud SQL (PostgreSQL)

| Tier | Instance Type | Storage | Est. Cost/month |
|------|---------------|---------|-----------------|
| Dev | db-f1-micro | 10 GB | $10 - $15 |
| Small | db-g1-small | 20 GB | $30 - $40 |
| Medium | db-custom-2-4096 | 50 GB | $80 - $100 |
| Large | db-custom-4-8192 | 100 GB | $200 - $300 |

**Pricing Details:**
- db-f1-micro: ~$7.67/month (shared vCPU, 0.6 GB RAM)
- db-g1-small: ~$25.55/month (shared vCPU, 1.7 GB RAM)
- Storage: $0.17/GB/month (SSD)
- Backups: $0.08/GB/month

### 3. NoSQL - Firestore

| Tier | Document Reads/day | Document Writes/day | Storage | Est. Cost/month |
|------|-------------------|---------------------|---------|-----------------|
| Dev | 50K | 20K | 1 GB | $0 (free tier) |
| Small | 500K | 100K | 5 GB | $5 - $10 |
| Medium | 2M | 500K | 20 GB | $30 - $50 |
| Large | 10M | 2M | 100 GB | $150 - $250 |

**Pricing Details:**
- Document reads: $0.06 per 100,000
- Document writes: $0.18 per 100,000
- Document deletes: $0.02 per 100,000
- Storage: $0.18/GB/month
- Free tier: 50K reads, 20K writes, 20K deletes, 1 GB storage per day

### 4. Caching - Memorystore (Redis)

| Tier | Capacity | Est. Cost/month |
|------|----------|-----------------|
| Dev | 1 GB Basic | $35 |
| Small | 1 GB Basic | $35 |
| Medium | 2 GB Standard | $140 |
| Large | 5 GB Standard | $350 |

**Pricing Details:**
- Basic tier: $0.049/GB/hour (~$35/GB/month)
- Standard tier (HA): $0.098/GB/hour (~$70/GB/month)

### 5. AI - Vertex AI (Gemini)

| Tier | Input Tokens/month | Output Tokens/month | Est. Cost/month |
|------|-------------------|---------------------|-----------------|
| Dev | 1M | 500K | $5 - $10 |
| Small | 10M | 5M | $50 - $80 |
| Medium | 50M | 25M | $200 - $350 |
| Large | 200M | 100M | $800 - $1,400 |

**Pricing Details (Gemini 1.5 Flash):**
- Input: $0.00001875 per 1K characters
- Output: $0.000075 per 1K characters

**Pricing Details (Gemini 1.5 Pro):**
- Input: $0.00125 per 1K characters
- Output: $0.00375 per 1K characters

**Note:** The platform uses Gemini for:
- Visual configuration generation
- RWAL narrative generation
- Quiz question generation
- Worked example generation

### 6. Messaging - Pub/Sub

| Tier | Messages/month | Est. Cost/month |
|------|----------------|-----------------|
| Dev | 100K | $0 (free tier) |
| Small | 1M | $0 - $5 |
| Medium | 10M | $10 - $20 |
| Large | 50M | $50 - $100 |

**Pricing Details:**
- Message ingestion: $40 per TiB
- Message delivery: $40 per TiB
- Free tier: 10 GB/month

### 7. Storage - Cloud Storage

| Tier | Storage | Egress | Est. Cost/month |
|------|---------|--------|-----------------|
| Dev | 5 GB | 10 GB | $1 - $2 |
| Small | 20 GB | 50 GB | $5 - $10 |
| Medium | 100 GB | 200 GB | $20 - $40 |
| Large | 500 GB | 1 TB | $80 - $150 |

**Pricing Details:**
- Standard storage: $0.020/GB/month
- Nearline storage: $0.010/GB/month
- Egress: $0.12/GB (after 1 GB free)
- CDN egress: $0.08/GB

### 8. Networking - Cloud CDN

| Tier | Cache Egress/month | Est. Cost/month |
|------|-------------------|-----------------|
| Dev | 10 GB | $1 - $2 |
| Small | 50 GB | $4 - $6 |
| Medium | 200 GB | $16 - $20 |
| Large | 1 TB | $80 - $100 |

**Pricing Details:**
- Cache egress (North America): $0.08/GB
- Cache fill: $0.01/GB
- HTTP/HTTPS requests: $0.0075 per 10,000

### 9. Monitoring & Logging

| Tier | Log Volume/month | Est. Cost/month |
|------|-----------------|-----------------|
| Dev | 5 GB | $0 (free tier) |
| Small | 20 GB | $5 - $10 |
| Medium | 100 GB | $50 - $75 |
| Large | 500 GB | $250 - $375 |

**Pricing Details:**
- Log ingestion: $0.50/GB (after 50 GB free)
- Log storage: $0.01/GB/month
- Metrics: $0.258 per 1,000 time series

## Cost Optimization Strategies

### 1. Use Committed Use Discounts

- **Cloud SQL**: Up to 57% discount with 3-year commitment
- **Memorystore**: Up to 30% discount with 1-year commitment
- **Compute**: Up to 57% discount with committed use

### 2. Implement Auto-Scaling

```yaml
# Cloud Run auto-scaling configuration
autoscaling:
  minInstances: 0  # Scale to zero when idle
  maxInstances: 10
  targetCPUUtilization: 80
```

### 3. Use Appropriate Storage Classes

- Use **Standard** for frequently accessed content
- Use **Nearline** for content accessed < 1/month
- Use **Coldline** for backups and archives

### 4. Optimize AI Usage

- Cache AI-generated content (visual configs, RWAL narratives)
- Use Gemini Flash instead of Pro for most operations
- Batch requests where possible

### 5. Set Budget Alerts

```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="CBSE Learning Platform Budget" \
  --budget-amount=500USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Free Tier Benefits

GCP offers generous free tiers that can significantly reduce costs for development and small deployments:

| Service | Free Tier |
|---------|-----------|
| Cloud Run | 2M requests, 360K GiB-seconds, 180K vCPU-seconds/month |
| Firestore | 50K reads, 20K writes, 1 GB storage/day |
| Cloud Storage | 5 GB Standard storage, 1 GB egress/month |
| Pub/Sub | 10 GB/month |
| Cloud Logging | 50 GB/month |
| Cloud Build | 120 build-minutes/day |

## Sample Monthly Budget (Medium School - 500 Students)

| Service | Configuration | Cost |
|---------|--------------|------|
| Cloud Run (Backend) | 2 vCPU, 2 GB, 5M requests | $120 |
| Cloud SQL | db-custom-2-4096, 50 GB | $90 |
| Firestore | 2M reads, 500K writes, 20 GB | $40 |
| Memorystore | 2 GB Standard | $140 |
| Vertex AI | 50M input, 25M output tokens | $250 |
| Cloud Storage | 100 GB + CDN | $30 |
| Pub/Sub | 10M messages | $15 |
| Monitoring | 100 GB logs | $60 |
| **Total** | | **$745/month** |

## ROI Considerations

### Cost per Student

| Scale | Monthly Cost | Students | Cost/Student/Month |
|-------|-------------|----------|-------------------|
| Small | $200 | 100 | $2.00 |
| Medium | $750 | 500 | $1.50 |
| Large | $1,500 | 2000 | $0.75 |

### Value Delivered

- Personalized AI-driven learning experience
- Adaptive assessments based on Bloom's taxonomy
- Real-world application scenarios (SGT)
- Comprehensive progress tracking
- Scalable to all CBSE subjects and classes

## Contact for Custom Pricing

For enterprise deployments or custom requirements, consider:
- Google Cloud Partner discounts
- Education sector pricing
- Sustained use discounts
- Custom machine types

For questions about this budget estimate, please open an issue on GitHub.
