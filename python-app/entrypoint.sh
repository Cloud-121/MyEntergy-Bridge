#!/bin/bash

echo "MyEntergy_USERNAME: $MyEntergy_USERNAME"
echo "MyEntergy_PASSWORD: $MyEntergy_PASSWORD"
echo "MyEntergy_TIMEOUT: $MyEntergy_TIMEOUT"
echo "MyEntergy_DEBUG: $MyEntergy_DEBUG"
echo "mqtt_host: $mqtt_host"
echo "mqtt_port: $mqtt_port"
echo "mqtt_user: $mqtt_user"
echo "mqtt_password: $mqtt_password"
echo "mqtt_topic: $mqtt_topic"

# Set up the Python environment
source /app/venv/bin/activate

# Build the command
CMD="python run.py"

if [[ -n "$MyEntergy_USERNAME" ]]; then
    CMD+=" --username $MyEntergy_USERNAME"
fi
if [[ -n "$MyEntergy_PASSWORD" ]]; then
    CMD+=" --password $MyEntergy_PASSWORD"
fi
if [[ -n "$MyEntergy_TIMEOUT" ]]; then
    CMD+=" --timeout $MyEntergy_TIMEOUT"
fi
if [[ -n "$MyEntergy_DEBUG" ]]; then
    CMD+=" --debug $MyEntergy_DEBUG"
fi
if [[ -n "$mqtt_host" ]]; then
    CMD+=" --host $mqtt_host"
fi
if [[ -n "$mqtt_port" ]]; then
    CMD+=" --mqtt_port $mqtt_port"
fi
if [[ -n "$mqtt_user" ]]; then
    CMD+=" --mqtt_user $mqtt_user"
fi
if [[ -n "$mqtt_password" ]]; then
    CMD+=" --mqtt_password $mqtt_password"
fi
if [[ -n "$mqtt_topic" ]]; then
    CMD+=" --mqtt_topic $mqtt_topic"
fi

# Log the command and execute
echo "Executing: $CMD"
exec $CMD
