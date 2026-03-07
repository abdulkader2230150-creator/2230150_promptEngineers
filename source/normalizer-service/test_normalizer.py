import json
from normalizer import normalize_payload


def print_normalized(schema_family: str, payload: dict, title: str) -> None:
    print("=" * 100)
    print(title)
    print("-" * 100)
    normalized = normalize_payload(schema_family, payload)
    print(json.dumps(normalized, indent=2))
    print(f"\nTotal normalized events: {len(normalized)}\n")


if __name__ == "__main__":
    greenhouse_temperature = {
        "sensor_id": "greenhouse_temperature",
        "captured_at": "2026-03-06T17:17:31.233365+00:00",
        "metric": "temperature_c",
        "value": 24.36,
        "unit": "C",
        "status": "ok"
    }

    hydroponic_ph = {
        "sensor_id": "hydroponic_ph",
        "captured_at": "2026-03-06T17:18:48.503468+00:00",
        "measurements": [
            {
                "metric": "ph",
                "value": 6.27,
                "unit": "pH"
            }
        ],
        "status": "ok"
    }

    water_tank_level = {
        "sensor_id": "water_tank_level",
        "captured_at": "2026-03-06T17:20:03.134425+00:00",
        "level_pct": 71.85,
        "level_liters": 2874,
        "status": "ok"
    }

    air_quality_pm25 = {
        "sensor_id": "air_quality_pm25",
        "captured_at": "2026-03-06T17:20:28.373355+00:00",
        "pm1_ug_m3": 10.72,
        "pm25_ug_m3": 15.03,
        "pm10_ug_m3": 23.65,
        "status": "ok"
    }

    air_quality_voc = {
        "sensor_id": "air_quality_voc",
        "captured_at": "2026-03-06T17:13:58.523453+00:00",
        "measurements": [
            {
                "metric": "voc_ppb",
                "value": 199.66,
                "unit": "ppb"
            },
            {
                "metric": "co2e_ppm",
                "value": 489.9,
                "unit": "ppm"
            }
        ],
        "status": "ok"
    }

    solar_array = {
        "topic": "mars/telemetry/solar_array",
        "event_time": "2026-03-06T17:50:43.452987+00:00",
        "subsystem": "solar_array",
        "power_kw": 134.74,
        "voltage_v": 381.1,
        "current_a": 353.56,
        "cumulative_kwh": 8597.123
    }

    radiation = {
        "topic": "mars/telemetry/radiation",
        "event_time": "2026-03-06T17:52:03.464261+00:00",
        "source": {
            "system": "radiation-monitor",
            "segment": "habitat-alpha"
        },
        "measurements": [
            {
                "metric": "radiation_uSv_h",
                "value": 0.31,
                "unit": "uSv/h"
            }
        ],
        "status": "ok"
    }

    thermal_loop = {
        "topic": "mars/telemetry/thermal_loop",
        "event_time": "2026-03-06T17:52:53.475827+00:00",
        "loop": "primary",
        "temperature_c": 55.15,
        "flow_l_min": 118.08,
        "status": "ok"
    }

    airlock = {
        "topic": "mars/telemetry/airlock",
        "event_time": "2026-03-06T17:53:58.485990+00:00",
        "airlock_id": "airlock-1",
        "cycles_per_hour": 0.61,
        "last_state": "PRESSURIZING"
    }

    print_normalized("rest.scalar.v1", greenhouse_temperature, "REST SCALAR: greenhouse_temperature")
    print_normalized("rest.chemistry.v1", hydroponic_ph, "REST CHEMISTRY: hydroponic_ph")
    print_normalized("rest.level.v1", water_tank_level, "REST LEVEL: water_tank_level")
    print_normalized("rest.particulate.v1", air_quality_pm25, "REST PARTICULATE: air_quality_pm25")
    print_normalized("rest.chemistry.v1", air_quality_voc, "REST CHEMISTRY: air_quality_voc")
    print_normalized("topic.power.v1", solar_array, "TOPIC POWER: solar_array")
    print_normalized("topic.environment.v1", radiation, "TOPIC ENVIRONMENT: radiation")
    print_normalized("topic.thermal_loop.v1", thermal_loop, "TOPIC THERMAL LOOP: thermal_loop")
    print_normalized("topic.airlock.v1", airlock, "TOPIC AIRLOCK: airlock")