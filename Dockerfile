# 🚀 UPGRADE: Use Python 3.11 (Fixes importlib crash)
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies (Force latest versions)
RUN pip install --upgrade pip
RUN pip install google-genai colorama requests

# Copy your script
COPY sauce.py /app/sauce.py

# Run it
ENTRYPOINT ["python", "/app/sauce.py"]