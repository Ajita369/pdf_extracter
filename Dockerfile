# Use amd64 Python
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy extractor script
COPY extract_outline.py ./

# Ensure the directories exist
RUN mkdir -p app/input app/output

# Run the extractor
ENTRYPOINT ["python", "extract_outline.py"]