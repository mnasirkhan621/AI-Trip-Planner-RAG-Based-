"""
AWS Lambda Handler for AI Trip Planner
Uses Mangum to adapt FastAPI for Lambda + API Gateway
"""

from mangum import Mangum
from app.api import app

# Create the Lambda handler
# Mangum adapts ASGI apps (like FastAPI) to work with AWS Lambda
handler = Mangum(app, lifespan="off")
