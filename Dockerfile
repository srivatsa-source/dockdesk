# Use a lightweight Python image
FROM python:3.9-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies (ADDED: requests)
RUN pip install google-generativeai colorama requests
# Copy your script
COPY sauce.py /app/sauce.py

# Run it
ENTRYPOINT ["python", "/app/sauce.py"]