import json
import os
import time
import pika


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "normalized_events_exchange"
QUEUE_NAME = "debug_events"


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


def callback(ch, method, properties, body):
    event = json.loads(body.decode())

    print("=" * 100, flush=True)
    print("Received normalized event:", flush=True)
    print(json.dumps(event, indent=2), flush=True)
    print(flush=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.exchange_declare(
    exchange=EXCHANGE_NAME,
    exchange_type="fanout",
    durable=True
    )
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"Waiting for messages in queue '{QUEUE_NAME}'...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()