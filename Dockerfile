# # Use Python 3.11 slim image
# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first for better caching
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Expose port
# EXPOSE 8000

# # Run the application
# CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM public.ecr.aws/lambda/python:3.11

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# --- FIX: Install Build Tools ---
# The Python 3.11 Lambda image uses Amazon Linux 2023, which uses 'dnf'.
# We need gcc and python3-devel to compile libraries like numpy and chromadb.
RUN dnf update -y && \
    dnf install -y gcc gcc-c++ python3-devel && \
    dnf clean all

# Upgrade pip to ensure it handles binary wheels correctly
RUN pip install --upgrade pip

# Install the python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (Check if your file is named app.py and function is lambda_handler)
CMD [ "app.lambda_handler" ]