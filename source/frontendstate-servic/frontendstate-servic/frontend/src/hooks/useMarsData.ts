import { useState, useEffect, useCallback } from "react";

// --- TYPES & INTERFACES ---
export interface SensorData {
  id: string;
  name: string;
  metric_key: string;
  value: number;
  unit: string;
  history: number[];
  critical: boolean;
  criticalThreshold?: { min?: number; max?: number };
}

export interface ActuatorData {
  id: string;
  name: string;
  active: boolean;
}

export interface AutomationRule {
  id: string;
  sensorId: string;
  operator: string;
  threshold: number;
  actuatorId: string;
  targetState: boolean;
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const METRIC_FALLBACKS: Record<string, string[]> = {
  entrance_humidity: ["humidity_pct", "humidity_percentage"],
  hydroponic_ph: ["ph", "ph_level"],
  water_tank_level: ["level_pct", "level_percentage"],
  air_quality_pm25: ["pm25_ug_m3", "pm25_ugm3"],
  corridor_pressure: ["pressure_kpa", "pressure_pa"],
};

// --- FULL INITIAL STATE (Restoring all your original devices) ---
const initSensors = (): SensorData[] => [
  { id: "greenhouse_temperature", metric_key: "temperature_c", name: "Greenhouse Temp", value: 0, unit: "C", history: [], critical: false, criticalThreshold: { max: 28 } },
  { id: "entrance_humidity", metric_key: "humidity_pct", name: "Entrance Humidity", value: 0, unit: "%", history: [], critical: false, criticalThreshold: { max: 70 } },
  { id: "co2_hall", metric_key: "co2_ppm", name: "CO2 Hall", value: 0, unit: "ppm", history: [], critical: false, criticalThreshold: { max: 1000 } },
  { id: "hydroponic_ph", metric_key: "ph", name: "Hydroponic pH", value: 0, unit: "pH", history: [], critical: false, criticalThreshold: { min: 5.5, max: 7.5 } },
  { id: "water_tank_level", metric_key: "level_pct", name: "Water Tank Level", value: 0, unit: "%", history: [], critical: false, criticalThreshold: { min: 20 } },
  { id: "corridor_pressure", metric_key: "pressure_kpa", name: "Corridor Pressure", value: 0, unit: "kPa", history: [], critical: false, criticalThreshold: { min: 90, max: 110 } },
  { id: "air_quality_pm25", metric_key: "pm25_ug_m3", name: "Air Quality PM2.5", value: 0, unit: "ug/m3", history: [], critical: false, criticalThreshold: { max: 35 } },
  { id: "air_quality_voc", metric_key: "voc_ppb", name: "Air Quality VOC", value: 0, unit: "ppb", history: [], critical: false, criticalThreshold: { max: 500 } },
];

const initActuators = (): ActuatorData[] => [
  { id: "cooling_fan", name: "Cooling Fan", active: false },
  { id: "entrance_humidifier", name: "Entrance Humidifier", active: false },
  { id: "hall_ventilation", name: "Hall Ventilation", active: false },
  { id: "habitat_heater", name: "Habitat Heater", active: false },
];

export function useMarsData() {
  const [sensors, setSensors] = useState<SensorData[]>(initSensors);
  const [actuators, setActuators] = useState<ActuatorData[]>(initActuators);
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [solTime, setSolTime] = useState({ sol: 847, time: "14:32:07" });

  useEffect(() => {
    const clockInterval = setInterval(() => {
      setSolTime(prev => {
        const parts = prev.time.split(":").map(Number);
        // Advance by 1 second every second
        const totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2] + 1;

        const h = String(Math.floor(totalSeconds / 3600) % 25).padStart(2, "0");
        const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
        const s = String(totalSeconds % 60).padStart(2, "0");

        return { ...prev, time: `${h}:${m}:${s}` };
      });
    }, 1000);

    return () => clearInterval(clockInterval);
  }, []);

  // 1. POLLING THE STATE SERVICE
  useEffect(() => {
    const fetchLatestState = async () => {
      try {
        const response = await fetch(`${API_BASE}/state`);
        if (!response.ok) throw new Error("State Service Down");

        const latestData = await response.json();

        setSensors(prev => prev.map(s => {
          // Key format: "source_name.metric" from state_consumer.py
          const key = `${s.id}.${s.metric_key}`;
          let remoteSensor = latestData[key];

          if (!remoteSensor) {
            const fallbacks = METRIC_FALLBACKS[s.id] ?? [];
            for (const alt of fallbacks) {
              const altKey = `${s.id}.${alt}`;
              if (latestData[altKey]) {
                remoteSensor = latestData[altKey];
                break;
              }
            }
          }

          if (remoteSensor) {
            const newVal = Number(remoteSensor.value);
            const isCritical = (s.criticalThreshold?.max != null && newVal > s.criticalThreshold.max) ||
                               (s.criticalThreshold?.min != null && newVal < s.criticalThreshold.min);
            return {
              ...s,
              value: newVal,
              history: [...s.history.slice(-19), newVal], // Keeps chart history updated
              critical: isCritical,
            };
          }
          return s;
        }));
      } catch (e) {
        console.error("Connection Error:", e);
      }
    };

    const interval = setInterval(fetchLatestState, 1000);
    return () => clearInterval(interval);
  }, []);

  // 1a. POLLING ACTUATOR STATES
  useEffect(() => {
    const fetchActuators = async () => {
      try {
        const response = await fetch(`${API_BASE}/actuators`);
        if (!response.ok) throw new Error("Actuators Service Down");
        const data = await response.json();
        const actuatorMap = data.actuators ?? data;
        if (!actuatorMap || typeof actuatorMap !== "object") return;

        setActuators(prev => prev.map(a => {
          const remote = actuatorMap[a.id];
          if (remote == null) return a;
          const active = String(remote).toUpperCase() === "ON";
          return { ...a, active };
        }));
      } catch (e) {
        console.error("Failed to fetch actuators:", e);
      }
    };

    fetchActuators();
    const interval = setInterval(fetchActuators, 2000);
    return () => clearInterval(interval);
  }, []);

  // 1b. LOAD EXISTING RULES
  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await fetch(`${API_BASE}/rules`);
        if (!response.ok) throw new Error("Rules Service Down");
        const data = await response.json();
        const mapped: AutomationRule[] = (data.rules || []).map((r: any) => ({
          id: r.rule_id,
          sensorId: r.source_name,
          operator: r.operator,
          threshold: Number(r.threshold_value),
          actuatorId: r.actuator_name,
          targetState: String(r.target_state).toUpperCase() === "ON",
        }));
        setRules(mapped);
      } catch (e) {
        console.error("Failed to load rules:", e);
      }
    };
    fetchRules();
  }, []);

  // 2. MANUAL ACTUATOR CONTROL
  const setActuatorState = useCallback(async (id: string, state: boolean) => {
    setActuators(prev => prev.map(a => a.id === id ? { ...a, active: state } : a));

    try {
      await fetch(`${API_BASE}/actuators/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: state ? "ON" : "OFF" }),
      });
    } catch (e) {
      console.error("Failed to toggle actuator:", e);
    }
  }, []);

  // 3. AUTOMATION RULES MANAGEMENT
  const addRule = useCallback(async (rule: Omit<AutomationRule, "id">) => {
    try {
      const response = await fetch(`${API_BASE}/rules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_name: rule.sensorId,
          metric: sensors.find(s => s.id === rule.sensorId)?.metric_key ?? "temperature_c",
          operator: rule.operator,
          threshold_value: rule.threshold,
          actuator_name: rule.actuatorId,
          target_state: rule.targetState ? "ON" : "OFF",
        }),
      });
      if (!response.ok) throw new Error("Failed to add rule");

      const result = await response.json();
      const newRule: AutomationRule = {
        id: result.rule_id ?? `${Date.now()}`,
        sensorId: rule.sensorId,
        operator: rule.operator,
        threshold: rule.threshold,
        actuatorId: rule.actuatorId,
        targetState: rule.targetState,
      };
      setRules(prev => [...prev, newRule]);
    } catch (e) {
      console.error("Failed to add rule:", e);
    }
  }, [sensors]);

  const removeRule = useCallback(async (id: string) => {
    try {
      await fetch(`${API_BASE}/rules/${id}`, { method: "DELETE" });
      setRules(prev => prev.filter(r => r.id !== id));
    } catch (e) {
      console.error("Failed to remove rule:", e);
    }
  }, []);

  return { sensors, actuators, rules, solTime, setActuatorState, addRule, removeRule };
}
