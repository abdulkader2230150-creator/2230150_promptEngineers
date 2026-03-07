import { type ActuatorData } from "@/hooks/useMarsData";
import { Power, PowerOff } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  actuators: ActuatorData[];
  onSetState: (id: string, state: boolean) => void;
}

export function ActuatorControls({ actuators, onSetState }: Props) {
  return (
    <section>
      <h2 className="text-sm font-display font-semibold text-muted-foreground uppercase tracking-wider mb-4">
        Manual Actuator Controls
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {actuators.map(a => (
          <div key={a.id} className="sensor-card flex flex-col items-center gap-3">
            <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">{a.name}</p>
            <span className={`text-lg font-mono font-bold ${a.active ? "text-neon-green" : "text-muted-foreground"}`}>
              {a.active ? "ON" : "OFF"}
            </span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={a.active ? "default" : "outline"}
                className={a.active ? "glow-green bg-neon-green/20 text-neon-green border-neon-green/40 hover:bg-neon-green/30" : ""}
                onClick={() => onSetState(a.id, true)}
              >
                <Power className="h-4 w-4" /> ON
              </Button>
              <Button
                size="sm"
                variant={!a.active ? "destructive" : "outline"}
                className={!a.active ? "glow-red" : ""}
                onClick={() => onSetState(a.id, false)}
              >
                <PowerOff className="h-4 w-4" /> OFF
              </Button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
