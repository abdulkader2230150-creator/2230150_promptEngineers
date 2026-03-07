import json
import requests


BASE_URL = "http://localhost:8080"

# Hardcoded mapping from sensor/topic name to schema family
# Based on the simulator brief and schema contract.
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
    """
    Fetch one REST sensor payload from the simulator.
    """
    url = f"{BASE_URL}/api/sensors/{sensor_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def wrap_raw_message(schema_family: str, payload: dict) -> dict:
    """
    Wrap the raw simulator payload in the agreed raw broker message format.
    """
    return {
        "schema_family": schema_family,
        "payload": payload
    }


def print_wrapped_message(sensor_id: str) -> None:
    """
    Fetch one sensor payload, wrap it, and print it nicely.
    """
    schema_family = REST_SENSOR_SCHEMA_MAP[sensor_id]
    payload = fetch_sensor(sensor_id)
    wrapped = wrap_raw_message(schema_family, payload)

    print("=" * 100)
    print(f"SENSOR: {sensor_id}")
    print("-" * 100)
    print(json.dumps(wrapped, indent=2))
    print()


if __name__ == "__main__":
    # Start with a few real sensors you already tested
    sensors_to_test = [
        "greenhouse_temperature",
        "hydroponic_ph",
        "water_tank_level",
        "air_quality_pm25",
        "air_quality_voc",
    ]

    for sensor_id in sensors_to_test:
        print_wrapped_message(sensor_id)