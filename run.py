import argparse
import time
import json
from client import get_current_kwh_usage
from paho.mqtt import client as mqtt_client
import os
from datetime import datetime

# Configuration via argparse
parser = argparse.ArgumentParser(description="MyEntergy Script with MQTT Support")
parser.add_argument("--username", required=True, help="Entergy username")
parser.add_argument("--password", required=True, help="Entergy password")
parser.add_argument("--host", required=True, help="MQTT broker host")
parser.add_argument("--clientid", default="myentergy", help="MQTT client ID")
parser.add_argument("--timeout", type=int, default=10, help="Interval in minutes to fetch power usage")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--mqtt_port", type=int, default=1883, help="MQTT broker port")
parser.add_argument("--mqtt_user", help="MQTT username")
parser.add_argument("--mqtt_password", help="MQTT password")
parser.add_argument("--mqtt_topic", default="homeassistant/sensor/energy_kwh", help="MQTT topic for publishing energy data")

args = parser.parse_args()

#variables
last_reset_time = None

# Variables
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def connect_mqtt():
    """Connect to the MQTT broker and set up event handlers."""
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
            # Publish Home Assistant discovery configuration
            last_reset_time = datetime.utcnow().isoformat()
            discovery_payload = {
                "name": "Current Energy Usage",
                "state_topic": f"{args.mqtt_topic}/state",
                "availability_topic": f"{args.mqtt_topic}/availability",
                "unit_of_measurement": "kWh",
                "device_class": "energy",  # Correct device class
                "last_reset": last_reset_time,  # Set to appropriate value
                "state_class": "total_increasing",  # Or "total_increasing" if cumulative
                "unique_id": "energy_kwh_sensor",
                "device": {
                    "identifiers": ["energy_monitor_device"],
                    "name": "Energy Monitor",
                    "model": "Entergy Sensor",
                    "manufacturer": "MyEntergy"
                }
            }

            client.publish(
                f"homeassistant/sensor/energy_kwh/config",
                json.dumps(discovery_payload),
                retain=True
            )
        else:
            print(f"Failed to connect to MQTT Broker, return code {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"Disconnected from MQTT Broker with result code {rc}")
        handle_reconnect(client)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, args.clientid)
    client.username_pw_set(args.mqtt_user, args.mqtt_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.will_set(f"{args.mqtt_topic}/availability", "offline", retain=True)
    client.connect(args.host, args.mqtt_port, keepalive=60)
    return client

def handle_reconnect(client):
    """Handle MQTT reconnect logic with exponential backoff."""
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        print(f"Reconnecting in {reconnect_delay} seconds...")
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected to MQTT Broker")
            return
        except Exception as err:
            print(f"Reconnection failed: {err}")

        reconnect_delay = min(reconnect_delay * RECONNECT_RATE, MAX_RECONNECT_DELAY)
        reconnect_count += 1

    print("Max reconnection attempts reached. Exiting...")
    exit(1)

def main():
    """Main function to fetch power usage and publish to MQTT."""
    client = connect_mqtt()
    client.loop_start()

    # Set availability to online
    client.publish(f"{args.mqtt_topic}/availability", "online", retain=True)

    try:
        while True:
            print("Fetching current kWh usage...")
            try:
                power_usage = get_current_kwh_usage(args.username, args.password)
            except Exception as e:
                print(f"Error while fetching power usage: {e}")
                print("Retrying in 10 minutes...")
                timeout_wait = 600
                start_time = time.time()
                while time.time() - start_time < timeout_wait:
                    if args.debug:
                        print(f"Debug: Sleeping for 1 second with remaining time: {timeout_wait - (time.time() - start_time)} seconds")
                    time.sleep(1)
                try:
                    power_usage = get_current_kwh_usage(args.username, args.password)
                except Exception as e:
                    print(f"Error while fetching power usage: {e}")



            # Publish power usage
            try:
                result = client.publish(
                    f"{args.mqtt_topic}/state",
                    power_usage,  # Sending raw power value, no JSON wrapping
                    retain=True
                )
                # Check if publish was successful
                status = result[0]
                if status == 0:
                    print(f"Message sent to topic `{args.mqtt_topic}/state`: {power_usage}")
                else:
                    print(f"Failed to send message to topic `{args.mqtt_topic}/state`")
            except Exception as e:
                print(f"Error while publishing message: {e}")

            if args.debug:
                print(f"Debug: Sleeping for {args.timeout} minutes...")

            # Sleep in 1-second chunks to allow MQTT operations
            timeout_seconds = args.timeout * 60
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                if args.debug:
                    print(f"Debug: Sleeping for 1 second with remaining time: {timeout_seconds - (time.time() - start_time)} seconds")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting on user interrupt...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client.publish(f"{args.mqtt_topic}/availability", "offline", retain=True)
        client.loop_stop()
        client.disconnect()
        print("Cleanly disconnected from MQTT Broker.")

if __name__ == "__main__":
    main()
