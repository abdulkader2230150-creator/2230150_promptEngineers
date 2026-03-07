import json
import os
import time
import pika

from normalizer import normalize_payload


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RAW_QUEUE = "raw_events"
NORMALIZED_EXCHANGE = "normalized_events_exchange"


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

    channel.queue_declare(queue=RAW_QUEUE, durable=True)
    channel.exchange_declare(
    exchange=NORMALIZED_EXCHANGE,
    exchange_type="fanout",
    durable=True
    )

    def callback(ch, method, properties, body):
        raw_message = json.loads(body.decode())
        schema_family = raw_message["schema_family"]
        payload = raw_message["payload"]

        normalized_events = normalize_payload(schema_family, payload)

        print("=" * 100, flush=True)
        print("Received raw message:", flush=True)
        print(json.dumps(raw_message, indent=2), flush=True)
        print("\nNormalized events:", flush=True)
        print(json.dumps(normalized_events, indent=2), flush=True)
        print(f"\nTotal normalized events: {len(normalized_events)}\n", flush=True)

        for event in normalized_events:
            channel.basic_publish(
                exchange=NORMALIZED_EXCHANGE,
                routing_key="",
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2),
            )

        print(
            f"Published {len(normalized_events)} event(s) to exchange'{NORMALIZED_EXCHANGE}'", flush=True
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RAW_QUEUE, on_message_callback=callback)

    print(f"Waiting for messages in queue '{RAW_QUEUE}'...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()