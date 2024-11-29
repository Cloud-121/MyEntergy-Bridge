# Imports
from client import get_current_kwh_usage
import paho.mqtt.client as mqtt
import os

# Functions

def check_load(envload, name, default):
    if os.getenv(envload):
        {name} = os.getenv(envload)
    else:
        {name} = default

# Load environment variables from args

# Required environment variables

ENTERGY_USERNAME = os.getenv("ENTERGY_USERNAME")
ENTERGY_PASSWORD = os.getenv("ENTERGY_PASSWORD")
Host = os.getenv("MQTT_HOST")

# Optional environment variables

check_load("MQTT_PORT", "MQTT_PORT", 1883)
check_load("MQTT_USER", "MQTT_USER", "")
check_load("MQTT_PASSWORD", "MQTT_PASSWORD", "")
check_load("MQTT_TOPIC", "MQTT_TOPIC", "entergy")
check_load("Debug", "Debug", False)
check_load("timeout", "timeout", 32)


# mqtt handing
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(f"{topic}/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "entergy/usage":
        kwh_usage = get_current_kwh_usage(os.getenv("ENTERGY_USERNAME"), os.getenv("ENTERGY_PASSWORD"))
        client.publish("entergy/kwh", kwh_usage)
