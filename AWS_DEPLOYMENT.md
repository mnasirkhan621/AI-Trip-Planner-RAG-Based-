# AWS App Runner Deployment Guide

## Prerequisites

1. **AWS Account** with App Runner access
2. **AWS CLI** installed and configured
3. **GitHub repository** connected to AWS

## Deployment Options

### Option 1: Source-based Deployment (Recommended)

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner)

2. Click **Create service**

3. Select **Source code repository**
   - Connect your GitHub account
   - Select: `mnasirkhan621/AI-Trip-Planner-RAG-Based-`
   - Branch: `main`

4. Configure build settings:
   - Runtime: Python 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.api:app --host 0.0.0.0 --port 8000`
   - Port: `8000`

5. Add environment variable:
   - Key: `GOOGLE_API_KEY`
   - Value: Your Google Gemini API Key

6. Click **Create & deploy**

### Option 2: Container-based Deployment

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-trip-planner .
docker tag ai-trip-planner:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner:latest

# Create App Runner service
aws apprunner create-service \
  --service-name ai-trip-planner \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner:latest",
      "ImageRepositoryType": "ECR"
    }
  }'
```

## Configuration Files

| File | Purpose |
|------|---------|
| `apprunner.yaml` | App Runner configuration |
| `buildspec.yml` | CodeBuild specification |
| `Dockerfile` | Container definition |

## Environment Variables

Set these in App Runner console under "Configuration":

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API Key |

## Estimated Costs

- **App Runner**: ~$5-25/month for low traffic
- **First 12 months**: Free tier eligible (AWS Free Tier)

## Troubleshooting

1. **Build fails**: Check `requirements.txt` for missing dependencies
2. **Health check fails**: Ensure port 8000 is exposed
3. **API errors**: Verify `GOOGLE_API_KEY` is set correctly
