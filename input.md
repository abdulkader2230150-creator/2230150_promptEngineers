# SYSTEM DESCRIPTION:

MarsOps is a distributed platform designed to manage critical Martian habitat infrastructure in 2036. It ingests data from incompatible IoT devices, normalizing REST polling and asynchronous telemetry into a unified format, to power an event-driven automation engine. Through a real-time dashboard, operators can monitor systems and manage persistent "if-then" rules to trigger actuators, ensuring habitat stability and preventing "thermodynamic consequences." The system uses RabbitMQ for internal events, stores rules in SQLite, and maintains the latest sensor state in memory.

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
10. As an Operator, I want sensors to be visually grouped by type (e.g., "Power Bus" vs. "Life Support") and view their data according to this grouping for better organization
11. As an Operator, I want to create automation rules (e.g., "IF temp > 28 THEN fan ON") via the UI to maintain habitat stability.
12. As an Operator, I want to view a list of all active automation rules so that I know what logic is currently running.
13. As an Operator, I want to delete a rule that is no longer needed to prevent conflicting habitat commands.
14. As an Operator, I want my rules to persist even if the system restarts, so that automation doesn't fail after a power surge.
15. As an Operator, I want all sensor data to follow a standard format so that I can create automation rules without worrying about device-specific dialects.
16. As an Operator, I want my automation rules to be saved in a database  so that the habitat remains safe even if a specific service needs to restart.
17. As an Operator, I want duplicate rules to be ignored so that conflicting or repeated automation does not occur.

# STANDARD EVENT SCHEMA

{
  "event_id": "string",
  "source_type": "rest | telemetry",
  "source_name": "string",
  "schema_family": "string",
  "captured_at": "string (ISO-8601)",
  "metric": "string",
  "value": "number",
  "unit": "string",
  "status": "string",
  "metadata": { "key": "value" },
  "raw_payload": { "original": "payload" }
}

# RULE MODEL

{
  "rule_id": "string",
  "source_name": "string",
  "metric": "string",
  "operator": "< | <= | = | > | >=",
  "threshold_value": 0.0,
  "actuator_name": "string",
  "target_state": "ON | OFF"
}
