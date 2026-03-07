import { type SensorData } from "@/hooks/useMarsData";
import { Sparkline } from "./Sparkline";

interface Props {
  sensor: SensorData;
}

export function SensorCard({ sensor }: Props) {
  return (
    <div className={`sensor-card ${sensor.critical ? "sensor-card-critical border-neon-red" : "hover:border-primary/40"}`}>
      <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider mb-2">
        {sensor.name}
      </p>
      <p className={`text-3xl font-mono font-bold tracking-tight ${sensor.critical ? "text-neon-red" : "text-foreground"}`}>
        {sensor.id === "corridor_pressure" ? sensor.value.toLocaleString() : sensor.value}
        <span className="text-sm font-normal text-muted-foreground ml-1">{sensor.unit}</span>
      </p>
      <div className="mt-3">
        <Sparkline data={sensor.history} critical={sensor.critical} />
      </div>
    </div>
  );
}
