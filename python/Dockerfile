# Dockerfile for Elfa MCP Server

FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY python/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY python/ .

# Set environment variable for API key
# This will be overridden when running the container
ENV ELFA_API_KEY=""

# Run the server
ENTRYPOINT ["python", "-m", "elfa_mcp.server"]