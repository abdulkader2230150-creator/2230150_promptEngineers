import json
import os
import threading
import time

import pika
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "normalized_events_exchange"
QUEUE_NAME = "api_state_events"
SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://host.docker.internal:8080")

app = FastAPI(title="Mars Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_state = {}


class RuleCreate(BaseModel):
    source_name: str
    metric: str
    operator: str
    threshold_value: float
    actuator_name: str
    target_state: str


class ActuatorCommand(BaseModel):
    state: str


def build_state_key(event: dict) -> str:
    return f"{event['source_name']}.{event['metric']}"


def update_latest_state(event: dict) -> None:
    key = build_state_key(event)
    latest_state[key] = {
        "source_type": event["source_type"],
        "source_name": event["source_name"],
        "schema_family": event["schema_family"],
        "metric": event["metric"],
        "value": event["value"],
        "unit": event["unit"],
        "status": event["status"],
        "captured_at": event["captured_at"],
        "metadata": event.get("metadata", {}),
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
            print(f"RabbitMQ not ready yet: {repr(e)}", flush=True)
            time.sleep(3)


def consume_state_events():
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="fanout",
        durable=True
    )
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        try:
            event = json.loads(body.decode())
            update_latest_state(event)
        except Exception as e:
            print(f"Failed to process API state event: {e}", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"Backend API listening on queue '{QUEUE_NAME}'", flush=True)
    channel.start_consuming()


@app.on_event("startup")
def startup_event():
    db.init_db()

    thread = threading.Thread(target=consume_state_events, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/state")
def get_state():
    return latest_state


@app.get("/api/state")
def get_state_api():
    return latest_state


@app.get("/rules")
def get_rules():
    return {"rules": db.get_all_rules()}


@app.post("/rules")
def create_rule(rule: RuleCreate):
    rule_id = db.add_rule(
        source_name=rule.source_name,
        metric=rule.metric,
        operator=rule.operator,
        threshold_value=rule.threshold_value,
        actuator_name=rule.actuator_name,
        target_state=rule.target_state,
    )
    return {"message": "Rule created", "rule_id": rule_id}


@app.delete("/rules/{rule_id}")
def remove_rule(rule_id: str):
    deleted = db.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted", "rule_id": rule_id}


@app.get("/actuators")
def get_actuators():
    try:
        response = requests.get(f"{SIMULATOR_BASE_URL}/api/actuators", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch actuators: {e}")


@app.post("/actuators/{actuator_name}")
def set_actuator(actuator_name: str, command: ActuatorCommand):
    try:
        response = requests.post(
            f"{SIMULATOR_BASE_URL}/api/actuators/{actuator_name}",
            json={"state": command.state},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set actuator: {e}")
