# Python Application Container (python-app/Dockerfile)
FROM python:3.9-slim

WORKDIR /app

# moving files

COPY requirments.txt /app/
COPY run.py /app/
COPY client.py /app/

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install system dependencies and Python dependencies
RUN apt-get update && apt-get install -y python3-venv
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --upgrade pip

RUN /app/venv/bin/pip install -r requirments.txt

# Set environment variables (pass these from Docker Compose)
ENV MyEntergy_USERNAME=${USERNAME}
ENV MyEntergy_PASSWORD=${PASSWORD}
ENV MyEntergy_TIMEOUT=${TIMEOUT}
ENV MyEntergy_DEBUG=${DEBUG}

ENV mqtt_host=${MQTT_HOST}
ENV mqtt_port=${MQTT_PORT}
ENV mqtt_user=${MQTT_USER}
ENV mqtt_password=${MQTT_PASSWORD}
ENV mqtt_topic=${MQTT_TOPIC}
ENV clientID=${CLIENT_ID}

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Default command to run the entrypoint script
CMD ["/bin/bash", "/entrypoint.sh"]
