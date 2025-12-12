# AWS Lambda Deployment Guide

## Prerequisites

1. **AWS CLI** installed and configured
2. **AWS SAM CLI** installed: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. **Docker** installed and running

## Quick Deploy (5 Steps)

### Step 1: Create ECR Repository
```bash
aws ecr create-repository --repository-name ai-trip-planner --region us-east-1
```

### Step 2: Build the Lambda Container
```bash
sam build --use-container
```

### Step 3: Deploy (First Time)
```bash
sam deploy --guided
```

When prompted:
- **Stack Name**: `ai-trip-planner`
- **Region**: `us-east-1`
- **GoogleApiKey**: Enter your Google Gemini API Key
- **Confirm changes**: `y`
- **Allow SAM CLI to create IAM roles**: `y`
- **Save arguments to samconfig.toml**: `y`

### Step 4: Get Your API URL
After deployment, note the **ApiEndpoint** output:
```
https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
```

### Step 5: Test Your API
```bash
curl https://your-api-url.execute-api.us-east-1.amazonaws.com/prod/

curl -X POST https://your-api-url.execute-api.us-east-1.amazonaws.com/prod/plan_trip \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 2-day trip to Paris"}'
```

---

## Subsequent Deployments
```bash
sam build --use-container
sam deploy
```

---

## Local Testing
```bash
# Start local API (simulates Lambda + API Gateway)
sam local start-api

# Test locally
curl http://localhost:3000/
```

---

## Files Overview

| File | Purpose |
|------|---------|
| `lambda_handler.py` | Mangum adapter for FastAPI |
| `template.yaml` | SAM/CloudFormation template |
| `samconfig.toml` | SAM CLI configuration |
| `Dockerfile.lambda` | Lambda container image |

---

## Costs (Estimated)

| Resource | Cost |
|----------|------|
| Lambda | ~$0.20 per 1M requests |
| API Gateway | ~$3.50 per 1M requests |
| ECR | ~$0.10/GB/month |

**Free Tier**: 1M Lambda requests/month free

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Timeout | Increase `Timeout` in template.yaml |
| Memory error | Increase `MemorySize` (max 10240MB) |
| Cold start slow | Use Provisioned Concurrency |
| Package too large | Use container image (already configured) |
