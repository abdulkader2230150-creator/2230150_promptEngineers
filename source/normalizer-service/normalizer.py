import uuid
from copy import deepcopy
from typing import Any, Dict, List


def make_event(
    *,
    source_type: str,
    source_name: str,
    schema_family: str,
    captured_at: str,
    metric: str,
    value: float,
    unit: str,
    status: str = "ok",
    metadata: Dict[str, Any] | None = None,
    raw_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build one normalized event using the unified internal schema.
    """
    return {
        "event_id": str(uuid.uuid4()),
        "source_type": source_type,
        "source_name": source_name,
        "schema_family": schema_family,
        "captured_at": captured_at,
        "metric": metric,
        "value": value,
        "unit": unit,
        "status": status,
        "metadata": metadata or {},
        "raw_payload": deepcopy(raw_payload) if raw_payload else {},
    }


def normalize_rest_scalar(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        make_event(
            source_type="rest",
            source_name=payload["sensor_id"],
            schema_family="rest.scalar.v1",
            captured_at=payload["captured_at"],
            metric=payload["metric"],
            value=payload["value"],
            unit=payload["unit"],
            status=payload.get("status", "ok"),
            metadata={},
            raw_payload=payload,
        )
    ]


def normalize_rest_chemistry(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    events = []
    for measurement in payload["measurements"]:
        events.append(
            make_event(
                source_type="rest",
                source_name=payload["sensor_id"],
                schema_family="rest.chemistry.v1",
                captured_at=payload["captured_at"],
                metric=measurement["metric"],
                value=measurement["value"],
                unit=measurement["unit"],
                status=payload.get("status", "ok"),
                metadata={},
                raw_payload=payload,
            )
        )
    return events


def normalize_rest_level(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    unit_map = {
        "level_pct": "%",
        "level_liters": "L",
    }

    events = []
    for field in ["level_pct", "level_liters"]:
        events.append(
            make_event(
                source_type="rest",
                source_name=payload["sensor_id"],
                schema_family="rest.level.v1",
                captured_at=payload["captured_at"],
                metric=field,
                value=payload[field],
                unit=unit_map[field],
                status=payload.get("status", "ok"),
                metadata={},
                raw_payload=payload,
            )
        )
    return events


def normalize_rest_particulate(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    particulate_fields = ["pm1_ug_m3", "pm25_ug_m3", "pm10_ug_m3"]

    events = []
    for field in particulate_fields:
        events.append(
            make_event(
                source_type="rest",
                source_name=payload["sensor_id"],
                schema_family="rest.particulate.v1",
                captured_at=payload["captured_at"],
                metric=field,
                value=payload[field],
                unit="ug/m3",
                status=payload.get("status", "ok"),
                metadata={},
                raw_payload=payload,
            )
        )
    return events


def normalize_topic_power(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    field_units = {
        "power_kw": "kW",
        "voltage_v": "V",
        "current_a": "A",
        "cumulative_kwh": "kWh",
    }

    metadata = {
        "subsystem": payload["subsystem"]
    }

    events = []
    for field, unit in field_units.items():
        events.append(
            make_event(
                source_type="telemetry",
                source_name=payload["topic"],
                schema_family="topic.power.v1",
                captured_at=payload["event_time"],
                metric=field,
                value=payload[field],
                unit=unit,
                status=payload.get("status", "ok"),
                metadata=metadata,
                raw_payload=payload,
            )
        )
    return events


def normalize_topic_environment(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = {
        "system": payload["source"]["system"],
        "segment": payload["source"]["segment"],
    }

    events = []
    for measurement in payload["measurements"]:
        events.append(
            make_event(
                source_type="telemetry",
                source_name=payload["topic"],
                schema_family="topic.environment.v1",
                captured_at=payload["event_time"],
                metric=measurement["metric"],
                value=measurement["value"],
                unit=measurement["unit"],
                status=payload.get("status", "ok"),
                metadata=metadata,
                raw_payload=payload,
            )
        )
    return events


def normalize_topic_thermal_loop(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = {
        "loop": payload["loop"]
    }

    field_units = {
        "temperature_c": "C",
        "flow_l_min": "L/min",
    }

    events = []
    for field, unit in field_units.items():
        events.append(
            make_event(
                source_type="telemetry",
                source_name=payload["topic"],
                schema_family="topic.thermal_loop.v1",
                captured_at=payload["event_time"],
                metric=field,
                value=payload[field],
                unit=unit,
                status=payload.get("status", "ok"),
                metadata=metadata,
                raw_payload=payload,
            )
        )
    return events


def normalize_topic_airlock(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = {
        "airlock_id": payload["airlock_id"],
        "last_state": payload["last_state"],
    }

    return [
        make_event(
            source_type="telemetry",
            source_name=payload["topic"],
            schema_family="topic.airlock.v1",
            captured_at=payload["event_time"],
            metric="cycles_per_hour",
            value=payload["cycles_per_hour"],
            unit="cycles/hour",
            status=payload.get("status", "ok"),
            metadata=metadata,
            raw_payload=payload,
        )
    ]


def normalize_payload(schema_family: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Dispatch to the correct normalization function based on schema family.
    """
    dispatch = {
        "rest.scalar.v1": normalize_rest_scalar,
        "rest.chemistry.v1": normalize_rest_chemistry,
        "rest.level.v1": normalize_rest_level,
        "rest.particulate.v1": normalize_rest_particulate,
        "topic.power.v1": normalize_topic_power,
        "topic.environment.v1": normalize_topic_environment,
        "topic.thermal_loop.v1": normalize_topic_thermal_loop,
        "topic.airlock.v1": normalize_topic_airlock,
    }

    if schema_family not in dispatch:
        raise ValueError(f"Unsupported schema family: {schema_family}")

    return dispatch[schema_family](payload)