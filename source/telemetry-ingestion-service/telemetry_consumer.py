import json
import os
import threading
import time

import pika
import requests


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://localhost:8080")
RAW_QUEUE = "raw_events"

TOPIC_SCHEMA_MAP = {
    "mars/telemetry/solar_array": "topic.power.v1",
    "mars/telemetry/radiation": "topic.environment.v1",
    "mars/telemetry/life_support": "topic.environment.v1",
    "mars/telemetry/thermal_loop": "topic.thermal_loop.v1",
    "mars/telemetry/power_bus": "topic.power.v1",
    "mars/telemetry/power_consumption": "topic.power.v1",
    "mars/telemetry/airlock": "topic.airlock.v1",
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


def stream_topic(topic: str, schema_family: str) -> None:
    url = f"{SIMULATOR_BASE_URL}/api/telemetry/stream/{topic}"
    headers = {"Accept": "text/event-stream"}

    while True:
        connection = None
        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()
            channel.queue_declare(queue=RAW_QUEUE, durable=True)

            print(f"Subscribing to SSE topic: {topic}", flush=True)

            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=(5, None),
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                    if not line:
                        continue
                    if line.startswith(":"):
                        continue
                    if not line.startswith("data:"):
                        continue

                    data_str = line[len("data:"):].strip()
                    if not data_str:
                        continue

                    try:
                        payload = json.loads(data_str)
                    except Exception as e:
                        print(f"[WARN] {topic} invalid JSON: {e} -> {data_str}", flush=True)
                        continue

                    raw_message = {
                        "schema_family": schema_family,
                        "payload": payload,
                    }

                    channel.basic_publish(
                        exchange="",
                        routing_key=RAW_QUEUE,
                        body=json.dumps(raw_message),
                        properties=pika.BasicProperties(delivery_mode=2),
                    )

                    print(f"[SSE] {topic} -> published raw message", flush=True)
        except Exception as e:
            print(f"[ERROR] Stream error for {topic}: {e}", flush=True)
            time.sleep(3)
        finally:
            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass


def main() -> None:
    threads = []
    for topic, schema_family in TOPIC_SCHEMA_MAP.items():
        thread = threading.Thread(
            target=stream_topic,
            args=(topic, schema_family),
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
