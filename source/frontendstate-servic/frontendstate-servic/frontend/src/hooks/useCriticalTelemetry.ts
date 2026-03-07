import { useState, useEffect } from "react";

// --- TYPES ---
export interface CriticalSensor {
  id: string;
  name: string;
  group: "power" | "environment" | "access";
  value: number;
  unit: string;
  history: number[];
  status: "nominal" | "warning" | "critical";
  icon: string;
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

// Helper to calculate status based on thresholds
function getStatus(value: number, config: any): "nominal" | "warning" | "critical" {
  if (config.metric_keys && config.metric_keys.includes("cycles_per_hour")) {
    if (value <= 1) return "nominal";
    if (value <= 2) return "warning";
    return "critical";
  }
  if (value >= config.nominal[0] && value <= config.nominal[1]) return "nominal";
  if (value >= config.warning[0] && value <= config.warning[1]) return "warning";
  return "critical";
}

// --- CONFIGURATION ---
const configs = [
  {
    id: "solar_array",
    name: "Solar Array Output",
    group: "power",
    unit: "kW",
    nominal: [80, 160],
    warning: [60, 180],
    icon: "Sun",
    source_name: "mars/telemetry/solar_array",
    metric_keys: ["power_kw"],
  },
  {
    id: "power_bus",
    name: "Power Bus Voltage",
    group: "power",
    unit: "V",
    nominal: [360, 420],
    warning: [330, 440],
    icon: "Zap",
    source_name: "mars/telemetry/power_bus",
    metric_keys: ["voltage_v"],
  },
  {
    id: "power_consumption",
    name: "Power Consumption",
    group: "power",
    unit: "kW",
    nominal: [80, 200],
    warning: [60, 240],
    icon: "Activity",
    source_name: "mars/telemetry/power_consumption",
    metric_keys: ["power_kw"],
  },
  {
    id: "radiation",
    name: "Radiation Level",
    group: "environment",
    unit: "uSv/h",
    nominal: [0, 0.5],
    warning: [0.5, 1.5],
    icon: "RadioTower",
    source_name: "mars/telemetry/radiation",
    metric_keys: ["radiation_uSv_h", "radiation_mSv_h", "radiation_msv_h"],
  },
  {
    id: "life_support",
    name: "Life Support O2",
    group: "environment",
    unit: "%",
    nominal: [19, 23],
    warning: [18, 24],
    icon: "Heart",
    source_name: "mars/telemetry/life_support",
    metric_keys: ["oxygen_percent", "o2_pct", "o2_percentage", "oxygen_pct"],
  },
  {
    id: "thermal_loop",
    name: "Thermal Loop Temp",
    group: "environment",
    unit: "C",
    nominal: [40, 60],
    warning: [30, 70],
    icon: "Thermometer",
    source_name: "mars/telemetry/thermal_loop",
    metric_keys: ["temperature_c"],
  },
  {
    id: "airlock",
    name: "Airlock Cycles",
    group: "access",
    unit: "cycles/hour",
    nominal: [0, 3],
    warning: [3, 6],
    icon: "ShieldCheck",
    source_name: "mars/telemetry/airlock",
    metric_keys: ["cycles_per_hour"],
  },
];

export function useCriticalTelemetry() {
  const [sensors, setSensors] = useState<CriticalSensor[]>(() =>
    configs.map(c => ({
      id: c.id,
      name: c.name,
      group: c.group as any,
      value: 0,
      unit: c.unit,
      history: [],
      status: "nominal",
      icon: c.icon,
    }))
  );

  useEffect(() => {
    const fetchCriticalData = async () => {
      try {
        const response = await fetch(`${API_BASE}/state`);
        if (!response.ok) throw new Error("State Service Down");

        const latestData = await response.json();

        setSensors(prev => prev.map(s => {
          const config = configs.find(c => c.id === s.id);
          if (!config) return s;

          let remoteData = null;
          for (const metric of config.metric_keys) {
            const key = `${config.source_name}.${metric}`;
            if (latestData[key]) {
              remoteData = latestData[key];
              break;
            }
          }

          if (remoteData) {
            const newVal = Number(remoteData.value);
            return {
              ...s,
              value: newVal,
              history: [...s.history.slice(-39), newVal],
              status: getStatus(newVal, config),
            };
          }
          return s;
        }));
      } catch (e) {
        console.error("Critical Telemetry fetch failed:", e);
      }
    };

    const interval = setInterval(fetchCriticalData, 1000);
    return () => clearInterval(interval);
  }, []);

  return { sensors };
}
