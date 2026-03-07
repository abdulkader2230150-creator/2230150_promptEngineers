# SYSTEM DESCRIPTION:

MarsOps is a distributed platform designed to manage critical Martian habitat infrastructure in 2036. It ingests data from incompatible IoT devices, normalizing REST polling and asynchronous telemetry into a unified format, to power an event-driven automation engine. Through a real-time dashboard, operators can monitor systems and manage persistent "if-then" rules to trigger actuators. The system is event-driven with RabbitMQ, persists rules in SQLite, and keeps the latest sensor state in memory.

# USER STORIES:

1. As an Operator, I want to see a real-time list of all sensor values (e.g., temperature, radiation) so that I can monitor habitat safety.
2. As an Operator, if a rule condition is true, I want the system to automatically send a POST command to turn the actuator ON or OFF.
3. As an Operator, I want a sensor's row to turn red if its status is "warning", so I easily spot problems.
4. As an Operator, I want to see a list of actuators and if they are ON or OFF.
5. As an Operator, I want the system to poll the REST sensors, so that I have their current data.
6. As an Operator, I want the system to read the telemetry streams, so I can get continuous updates.
7. As an Operator, I want to see the "latest state" of a sensor instantly when I open the dashboard, so I don't have to wait for the next update.
8. As an Operator, I want to manually toggle actuators (e.g., cooling_fan) ON or OFF from the UI to override automation in emergencies.
9. As an Operator, I want to see a live line chart for specific sensors (e.g., CO2 levels) to track trends while the dashboard is open.
10. As an Operator, I want sensors to be visually grouped by type (e.g., "Power Bus" vs. "Life Support") and view their data according to this grouping for better organization.
11. As an Operator, I want to create automation rules (e.g., "IF temp > 28 THEN fan ON") via the UI to maintain habitat stability.
12. As an Operator, I want to view a list of all active automation rules so that I know what logic is currently running.
13. As an Operator, I want to delete a rule that is no longer needed to prevent conflicting habitat commands.
14. As an Operator, I want my rules to persist even if the system restarts, so that automation doesn't fail after a power surge.
15. As an Operator, I want all sensor data to follow a standard format so that I can create automation rules without worrying about device-specific dialects.
16. As an Operator, I want my automation rules to be saved in a database so that the habitat remains safe even if a specific service needs to restart.
17. As an Operator, I want duplicate rules to be ignored so that conflicting or repeated automation does not occur.

# CONTAINERS:

## CONTAINER_NAME: Simulator

### DESCRIPTION:
Provided Mars IoT simulator container exposing REST sensors, telemetry streams, and actuator endpoints.

### USER STORIES:
5, 6, 2, 8

### PORTS:
8080:8080

### DESCRIPTION:
Exposes REST endpoints for sensors and actuators and SSE streams for telemetry topics. It is an external dependency and must not be modified.

### PERSISTENCE EVALUATION
Not applicable (external system).

### EXTERNAL SERVICES CONNECTIONS
None.

### MICROSERVICES:

#### MICROSERVICE: mars-iot-simulator
TYPE: external
DESCRIPTION: Simulator providing REST sensors, telemetry streams, and actuator endpoints.
PORTS: 8080
TECHNOLOGICAL SPECIFICATION: Provided Docker image (mars-iot-simulator:multiarch_v1).
SERVICE ARCHITECTURE: External black-box service with REST and SSE interfaces.

## CONTAINER_NAME: RabbitMQ

### DESCRIPTION:
Message broker used for internal event-driven communication between services.

### USER STORIES:
1, 2, 5, 6, 7, 15

### PORTS:
5672:5672 (AMQP)
15672:15672 (Management UI)

### DESCRIPTION:
Hosts durable queues and a fanout exchange. Raw events are published to the raw_events queue. Normalized events are published to the normalized_events_exchange fanout exchange and distributed to multiple queues (rule_events, state_events, api_state_events, debug_events).

### PERSISTENCE EVALUATION
Queues are durable; no long-term historical persistence is required by the project.

### EXTERNAL SERVICES CONNECTIONS
All internal services connect to RabbitMQ over AMQP.

### MICROSERVICES:

#### MICROSERVICE: rabbitmq
TYPE: middleware
DESCRIPTION: AMQP broker used for internal messaging.
PORTS: 5672, 15672
TECHNOLOGICAL SPECIFICATION: rabbitmq:3-management container.
SERVICE ARCHITECTURE: Message broker with queues and fanout exchange.

## CONTAINER_NAME: ingestion-service

### DESCRIPTION:
Polls REST sensors from the simulator and publishes raw messages to RabbitMQ.

### USER STORIES:
5, 1, 7

### PORTS:
None

### DESCRIPTION:
Periodically calls /api/sensors/{id} for all REST sensors, wraps payloads into the raw message format, and publishes to the raw_events queue.

### PERSISTENCE EVALUATION
None.

### EXTERNAL SERVICES CONNECTIONS
Simulator (REST), RabbitMQ (AMQP).

### MICROSERVICES:

#### MICROSERVICE: ingestion-service
TYPE: backend worker
DESCRIPTION: REST polling and publishing of raw messages.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, requests, pika.
SERVICE ARCHITECTURE: Single-file producer with periodic polling loop.

## CONTAINER_NAME: telemetry-ingestion-service

### DESCRIPTION:
Consumes telemetry via SSE and publishes raw messages to RabbitMQ.

### USER STORIES:
6, 1, 7

### PORTS:
None

### DESCRIPTION:
Subscribes to SSE streams for multiple topics, parses data events, wraps payloads as raw messages, and publishes to raw_events.

### PERSISTENCE EVALUATION
None.

### EXTERNAL SERVICES CONNECTIONS
Simulator (SSE), RabbitMQ (AMQP).

### MICROSERVICES:

#### MICROSERVICE: telemetry-ingestion-service
TYPE: backend worker
DESCRIPTION: SSE client and raw message publisher.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, requests (streaming), pika.
SERVICE ARCHITECTURE: Threaded SSE consumers, one per topic.

## CONTAINER_NAME: normalizer-service

### DESCRIPTION:
Normalizes raw messages into a unified event schema.

### USER STORIES:
15

### PORTS:
None

### DESCRIPTION:
Consumes raw_events, transforms payloads by schema_family, and publishes normalized events to a fanout exchange.

### PERSISTENCE EVALUATION
None.

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ (AMQP).

### MICROSERVICES:

#### MICROSERVICE: normalizer-service
TYPE: backend worker
DESCRIPTION: Message normalization pipeline.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, pika.
SERVICE ARCHITECTURE: Consumer + dispatcher functions for each schema family.

## CONTAINER_NAME: rule-engine-service

### DESCRIPTION:
Evaluates automation rules on normalized events and triggers actuators.

### USER STORIES:
2, 14, 16, 17

### PORTS:
None

### DESCRIPTION:
Consumes rule_events, evaluates threshold rules, and calls simulator actuator endpoints on match. Uses SQLite for rule persistence and deduplication.

### PERSISTENCE EVALUATION
Rules are stored in /data/rules.db (SQLite, shared volume).

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ (AMQP), Simulator (REST actuators), SQLite shared volume.

### MICROSERVICES:

#### MICROSERVICE: rule-engine
TYPE: backend worker
DESCRIPTION: Rule evaluation and actuator trigger service.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, pika, requests, sqlite3.
SERVICE ARCHITECTURE: Consumer with rule evaluation and HTTP actuator calls.

DB STRUCTURE:

**rules** : | rule_id | source_name | metric | operator | threshold_value | actuator_name | target_state |

## CONTAINER_NAME: state-service

### DESCRIPTION:
Maintains latest sensor state in memory from normalized events.

### USER STORIES:
1, 7

### PORTS:
None

### DESCRIPTION:
Consumes state_events and updates an in-memory latest_state map keyed by source_name.metric.

### PERSISTENCE EVALUATION
In-memory only; no persistence required.

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ (AMQP).

### MICROSERVICES:

#### MICROSERVICE: state-service
TYPE: backend worker
DESCRIPTION: Latest state cache updated by normalized events.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, pika.
SERVICE ARCHITECTURE: Consumer updating an in-memory dictionary.

## CONTAINER_NAME: backend-api

### DESCRIPTION:
Provides REST API for rules, state, and actuator proxying.

### USER STORIES:
1, 4, 7, 8, 11, 12, 13, 14, 16, 17

### PORTS:
8000:8000

### DESCRIPTION:
Consumes api_state_events to maintain latest state in memory. Exposes REST endpoints for rules CRUD, state retrieval, and actuator control. Uses SQLite for rule persistence.

### PERSISTENCE EVALUATION
Rules are stored in /data/rules.db (SQLite, shared volume).

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ (AMQP), Simulator (REST actuators), SQLite shared volume.

### MICROSERVICES:

#### MICROSERVICE: backend-api
TYPE: backend
DESCRIPTION: FastAPI service for rules, state, and actuators.
PORTS: 8000
TECHNOLOGICAL SPECIFICATION: Python 3.11, FastAPI, uvicorn, pika, requests, sqlite3.
SERVICE ARCHITECTURE: FastAPI app with background RabbitMQ consumer thread and SQLite access layer.

ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Health check | 1 |
| GET | /state | Latest state snapshot | 1, 7 |
| GET | /api/state | Latest state snapshot (alias) | 1, 7 |
| GET | /rules | List rules | 12 |
| POST | /rules | Create rule | 11 |
| DELETE | /rules/{rule_id} | Delete rule | 13 |
| GET | /actuators | List actuator states | 4 |
| POST | /actuators/{actuator_name} | Set actuator state | 2, 8 |

DB STRUCTURE:

**rules** : | rule_id | source_name | metric | operator | threshold_value | actuator_name | target_state |

## CONTAINER_NAME: debug-consumer

### DESCRIPTION:
Debug-only consumer that logs normalized events.

### USER STORIES:
None (debugging only).

### PORTS:
None

### DESCRIPTION:
Consumes debug_events and prints normalized events for troubleshooting.

### PERSISTENCE EVALUATION
None.

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ (AMQP).

### MICROSERVICES:

#### MICROSERVICE: debug-consumer
TYPE: backend worker
DESCRIPTION: Logging consumer for debugging.
PORTS: None
TECHNOLOGICAL SPECIFICATION: Python 3.11, pika.
SERVICE ARCHITECTURE: Simple consumer printing messages.

## CONTAINER_NAME: frontend

### DESCRIPTION:
Web dashboard for real-time monitoring and rule management.

### USER STORIES:
1, 3, 4, 7, 8, 9, 10, 11, 12, 13

### PORTS:
8081:80

### DESCRIPTION:
Single-page UI that polls the backend for state and actuators, displays live charts, and provides a rule management interface.

### PERSISTENCE EVALUATION
None.

### EXTERNAL SERVICES CONNECTIONS
Backend API (HTTP).

### MICROSERVICES:

#### MICROSERVICE: frontend
TYPE: frontend
DESCRIPTION: React SPA for monitoring and rule management.
PORTS: 8081
TECHNOLOGICAL SPECIFICATION: React, Vite, TypeScript, Tailwind CSS, shadcn/ui.
SERVICE ARCHITECTURE: SPA with hooks for state polling and UI components for dashboard widgets.

PAGES:

| Name | Description | Related Microservice | User Stories |
| ---- | ----------- | -------------------- | ------------ |
| / (Dashboard) | Real-time dashboard with sensors, telemetry, actuators, and rules | backend-api | 1, 3, 4, 7, 8, 9, 10, 11, 12, 13 |
