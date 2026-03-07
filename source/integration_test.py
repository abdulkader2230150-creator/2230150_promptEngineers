import json
import os
import sys
import requests

# Make Python able to import from the two service folders
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INGESTION_DIR = os.path.join(CURRENT_DIR, "ingestion-service")
NORMALIZER_DIR = os.path.join(CURRENT_DIR, "normalizer-service")

sys.path.append(INGESTION_DIR)
sys.path.append(NORMALIZER_DIR)

from normalizer import normalize_payload  # noqa: E402


BASE_URL = "http://localhost:8080"

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


def process_sensor(sensor_id: str) -> None:
    schema_family = REST_SENSOR_SCHEMA_MAP[sensor_id]
    payload = fetch_sensor(sensor_id)
    raw_message = wrap_raw_message(schema_family, payload)
    normalized_events = normalize_payload(
        raw_message["schema_family"],
        raw_message["payload"]
    )

    print("=" * 100)
    print(f"SENSOR: {sensor_id}")
    print("-" * 100)
    print("RAW MESSAGE:")
    print(json.dumps(raw_message, indent=2))
    print("\nNORMALIZED EVENTS:")
    print(json.dumps(normalized_events, indent=2))
    print(f"\nTotal normalized events: {len(normalized_events)}\n")


if __name__ == "__main__":
    sensors_to_test = [
        "greenhouse_temperature",
        "hydroponic_ph",
        "water_tank_level",
        "air_quality_pm25",
        "air_quality_voc",
    ]

    for sensor_id in sensors_to_test:
        process_sensor(sensor_id)