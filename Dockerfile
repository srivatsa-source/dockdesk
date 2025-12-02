# Use a lightweight Python image
FROM python:3.9-slim

# Prevent Python from buffering stdout/stderr (so you see logs immediately)
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install openai colorama

# Copy your script into the container
COPY sauce.py /app/sauce.py

# When the container starts, run this file
ENTRYPOINT ["python", "/app/sauce.py"]