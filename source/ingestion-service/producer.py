import json
import os
import time
import requests
import pika


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "raw_events"
BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://localhost:8080")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))

REST_SENSOR_SCHEMA_MAP = {
    "greenhouse_temperature": "rest.scalar.v1",
    "entrance_humidity": "rest.scalar.v1",
    "co2_hall": "rest.scalar.v1",
    "hydroponic_ph": "rest.chemistry.v1",
    "water_tank_level": "rest.level.v1",
    "corridor_pressure": "rest.scalar.v1",
    "air_quality_pm25": "rest.particulate.v1",
    "air_quality_voc": "rest.chemistry.v1",
}


def fetch_sensor(sensor_id: str) -> dict:
    url = f"{BASE_URL}/api/sensors/{sensor_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def wrap_raw_message(schema_family: str, payload: dict) -> dict:
    return {
        "schema_family": schema_family,
        "payload": payload
    }


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            print(f"Connected to RabbitMQ at {RABBITMQ_HOST}", flush=True)
            return connection
        except Exception as e:
            print(f"RabbitMQ not ready yet: {e}", flush=True)
            time.sleep(3)


def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    sensors_to_publish = [
        "greenhouse_temperature",
        "entrance_humidity",
        "co2_hall",
        "hydroponic_ph",
        "water_tank_level",
        "corridor_pressure",
        "air_quality_pm25",
        "air_quality_voc",
    ]

    while True:
        for sensor_id in sensors_to_publish:
            schema_family = REST_SENSOR_SCHEMA_MAP[sensor_id]
            try:
                payload = fetch_sensor(sensor_id)
            except Exception as e:
                print(f"[WARN] Failed to fetch {sensor_id}: {e}", flush=True)
                continue

            raw_message = wrap_raw_message(schema_family, payload)
            body = json.dumps(raw_message)

            try:
                channel.basic_publish(
                    exchange="",
                    routing_key=QUEUE_NAME,
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                print("=" * 100, flush=True)
                print(f"Published raw message for sensor: {sensor_id}", flush=True)
                print(body, flush=True)
                print(flush=True)
            except Exception as e:
                print(f"[ERROR] Publish failed: {e}. Reconnecting...", flush=True)
                try:
                    connection.close()
                except Exception:
                    pass
                connection = connect_to_rabbitmq()
                channel = connection.channel()
                channel.queue_declare(queue=QUEUE_NAME, durable=True)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
