import json
import os
import time
import pika
import requests

import db


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "normalized_events_exchange"
QUEUE_NAME = "rule_events"
SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://host.docker.internal:8080")


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


def evaluate_condition(sensor_value, operator, threshold):
    try:
        val = float(sensor_value)
        thresh = float(threshold)

        if operator == "<":
            return val < thresh
        if operator == "<=":
            return val <= thresh
        if operator == "=":
            return val == thresh
        if operator == ">":
            return val > thresh
        if operator == ">=":
            return val >= thresh
    except ValueError:
        return False

    return False


def trigger_actuator(actuator_name, target_state):
    url = f"{SIMULATOR_BASE_URL}/api/actuators/{actuator_name}"
    payload = {"state": target_state}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"[ACTION] {actuator_name} -> {target_state}", flush=True)
        else:
            print(f"[ERROR] Actuator call failed: {response.status_code} {response.text}", flush=True)
    except Exception as e:
        print(f"[CRITICAL] Simulator connection failed: {e}", flush=True)


def callback(ch, method, properties, body):
    try:
        event = json.loads(body.decode())

        source_name = event.get("source_name")
        metric = event.get("metric")
        value = event.get("value")

        print("=" * 100, flush=True)
        print("Received normalized event:", flush=True)
        print(json.dumps(event, indent=2), flush=True)

        rules = db.get_rules_by_source_and_metric(source_name, metric)

        if not rules:
            print(f"No rules for {source_name}.{metric}", flush=True)
        else:
            for rule in rules:
                operator = rule["operator"]
                threshold = rule["threshold_value"]
                actuator_name = rule["actuator_name"]
                target_state = rule["target_state"]

                if evaluate_condition(value, operator, threshold):
                    print(
                        f"[RULE MATCH] {source_name}.{metric} {operator} {threshold} -> {actuator_name}={target_state}",
                        flush=True
                    )
                    trigger_actuator(actuator_name, target_state)
                else:
                    print(
                        f"[NO MATCH] {source_name}.{metric} value={value} rule={operator} {threshold}",
                        flush=True
                    )

    except Exception as e:
        print(f"[ERROR] Failed processing message: {e}", flush=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    db.init_db()
    if os.getenv("SEED_DEMO_RULES", "false").lower() == "true":
        db.seed_demo_rules()

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
