import { useCriticalTelemetry, type CriticalSensor } from "@/hooks/useCriticalTelemetry";
import {
  Sun, Zap, Activity, RadioTower, Heart, Thermometer, ShieldCheck,
} from "lucide-react";

const iconMap: Record<string, React.ElementType> = {
  Sun, Zap, Activity, RadioTower, Heart, Thermometer, ShieldCheck,
};

const statusColors: Record<string, string> = {
  nominal: "border-neon-green/40",
  warning: "border-neon-amber/60",
  critical: "border-neon-red",
};

const statusGlow: Record<string, string> = {
  nominal: "shadow-[0_0_8px_hsl(var(--neon-green)/0.2)]",
  warning: "shadow-[0_0_12px_hsl(var(--neon-amber)/0.3)]",
  critical: "shadow-[0_0_16px_hsl(var(--neon-red)/0.4)]",
};

const statusTextColor: Record<string, string> = {
  nominal: "text-neon-green",
  warning: "text-neon-amber",
  critical: "text-neon-red",
};

const statusBadgeColor: Record<string, string> = {
  nominal: "bg-neon-green/15 text-neon-green",
  warning: "bg-neon-amber/15 text-neon-amber",
  critical: "bg-neon-red/15 text-neon-red",
};

function LiveWave({ data, status }: { data: number[]; status: string }) {
  if (data.length < 2) return <div className="h-10 w-full" />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const h = 40;
  const w = 200;
  const step = w / (data.length - 1);

  const points = data.map((v, i) => `${i * step},${h - ((v - min) / range) * (h - 6) - 3}`).join(" ");

  const strokeColor =
    status === "critical"
      ? "hsl(var(--neon-red))"
      : status === "warning"
      ? "hsl(var(--neon-amber))"
      : "hsl(var(--neon-cyan))";

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-10" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`wave-fill-${status}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={strokeColor} stopOpacity="0.15" />
          <stop offset="100%" stopColor={strokeColor} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={`0,${h} ${points} ${w},${h}`}
        fill={`url(#wave-fill-${status})`}
      />
      <polyline
        points={points}
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Glowing dot at end */}
      {data.length > 0 && (
        <circle
          cx={(data.length - 1) * step}
          cy={h - ((data[data.length - 1] - min) / range) * (h - 6) - 3}
          r="3"
          fill={strokeColor}
          className="animate-pulse"
        />
      )}
    </svg>
  );
}

function CriticalCard({ sensor }: { sensor: CriticalSensor }) {
  const Icon = iconMap[sensor.icon] || Activity;

  return (
    <div
      className={`bg-card border rounded-lg p-4 transition-all duration-200
        ${statusColors[sensor.status]} ${statusGlow[sensor.status]}
        ${sensor.status === "critical" ? "sensor-card-critical" : ""}
      `}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${statusTextColor[sensor.status]}`} />
          <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
            {sensor.name}
          </p>
        </div>
        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${statusBadgeColor[sensor.status]}`}>
          {sensor.status.toUpperCase()}
        </span>
      </div>

      <p className={`text-2xl font-mono font-bold tracking-tight ${statusTextColor[sensor.status]}`}>
        {sensor.value}
        <span className="text-sm font-normal text-muted-foreground ml-1">{sensor.unit}</span>
      </p>

      <div className="mt-2">
        <LiveWave data={sensor.history} status={sensor.status} />
      </div>

      {/* Scan line effect */}
      <div className="relative h-[1px] mt-2 overflow-hidden rounded-full bg-border">
        <div
          className="absolute h-full w-1/3 rounded-full animate-scan-line"
          style={{
            background: `linear-gradient(90deg, transparent, ${
              sensor.status === "critical"
                ? "hsl(var(--neon-red))"
                : sensor.status === "warning"
                ? "hsl(var(--neon-amber))"
                : "hsl(var(--neon-cyan))"
            }, transparent)`,
          }}
        />
      </div>
    </div>
  );
}

const groupLabels: Record<string, { label: string; color: string }> = {
  power: { label: "Power Systems", color: "text-neon-amber" },
  environment: { label: "Environment & Safety", color: "text-neon-green" },
  access: { label: "Access Control", color: "text-neon-cyan" },
};

export function CriticalTelemetry() {
  const { sensors } = useCriticalTelemetry();

  const groups = ["power", "environment", "access"] as const;

  return (
    <section>
      <div className="flex items-center gap-3 mb-4">
        <h2 className="text-sm font-display font-semibold text-muted-foreground uppercase tracking-wider">
          Live Telemetry
        </h2>
        <span className="flex items-center gap-1.5 text-[10px] font-mono text-neon-cyan">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-neon-cyan animate-pulse" />
          5s
        </span>
      </div>

      <div className="space-y-6">
        {groups.map(group => {
          const groupSensors = sensors.filter(s => s.group === group);
          const { label, color } = groupLabels[group];
          return (
            <div key={group}>
              <p className={`text-xs font-display font-medium ${color} mb-3`}>{label}</p>
              <div className={`grid gap-4 ${
                group === "access"
                  ? "grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 max-w-md"
                  : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
              }`}>
                {groupSensors.map(s => (
                  <CriticalCard key={s.id} sensor={s} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
