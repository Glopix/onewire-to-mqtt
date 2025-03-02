# Use lightweight Python base image
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install required system dependencies for w1thermsensor
#RUN apk add --no-cache gcc musl-dev linux-headers python3-dev libffi-dev

# Install required Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./onewire-to-mqtt.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Define entrypoint
ENTRYPOINT ["python3", "onewire-to-mqtt.py"]
