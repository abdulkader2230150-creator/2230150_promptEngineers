import { useState } from "react";
import { type AutomationRule, type SensorData, type ActuatorData } from "@/hooks/useMarsData";
import { Button } from "@/components/ui/button";
import { Trash2, Plus } from "lucide-react";

interface Props {
  rules: AutomationRule[];
  sensors: SensorData[];
  actuators: ActuatorData[];
  onAddRule: (rule: Omit<AutomationRule, "id">) => void;
  onRemoveRule: (id: string) => void;
}

const operators = ["<", "<=", "=", ">", ">="];

export function RuleManager({ rules, sensors, actuators, onAddRule, onRemoveRule }: Props) {
  const [sensorId, setSensorId] = useState(sensors[0]?.id || "");
  const [operator, setOperator] = useState(">");
  const [threshold, setThreshold] = useState("");
  const [actuatorId, setActuatorId] = useState(actuators[0]?.id || "");
  const [targetState, setTargetState] = useState("ON");

  const handleAdd = () => {
    if (!threshold) return;
    onAddRule({ sensorId, operator, threshold: +threshold, actuatorId, targetState: targetState === "ON" });
    setThreshold("");
  };

  const sensorName = (id: string) => sensors.find(s => s.id === id)?.name || id;
  const actuatorName = (id: string) => actuators.find(a => a.id === id)?.name || id;

  const selectClass = "bg-secondary border border-border rounded-md px-2 py-1.5 text-sm font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary";

  return (
    <section>
      <h2 className="text-sm font-display font-semibold text-muted-foreground uppercase tracking-wider mb-4">
        Automation Rule Manager
      </h2>

      {/* Add Rule Form */}
      <div className="flex flex-wrap items-center gap-2 mb-4 p-3 bg-secondary/50 rounded-lg border border-border">
        <span className="text-xs text-muted-foreground font-mono">IF</span>
        <select value={sensorId} onChange={e => setSensorId(e.target.value)} className={selectClass}>
          {sensors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={operator} onChange={e => setOperator(e.target.value)} className={selectClass}>
          {operators.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
        <input
          type="number"
          value={threshold}
          onChange={e => setThreshold(e.target.value)}
          placeholder="Value"
          className="bg-secondary border border-border rounded-md px-2 py-1.5 text-sm font-mono text-foreground w-20 focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <span className="text-xs text-muted-foreground font-mono">THEN set</span>
        <select value={actuatorId} onChange={e => setActuatorId(e.target.value)} className={selectClass}>
          {actuators.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        <span className="text-xs text-muted-foreground font-mono">to</span>
        <select value={targetState} onChange={e => setTargetState(e.target.value)} className={selectClass}>
          <option value="ON">ON</option>
          <option value="OFF">OFF</option>
        </select>
        <Button size="sm" onClick={handleAdd} className="glow-cyan">
          <Plus className="h-4 w-4" /> Add Rule
        </Button>
      </div>

      {/* Rules Table */}
      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-secondary/60">
              <th className="text-left px-4 py-2 text-xs font-mono text-muted-foreground uppercase">Condition</th>
              <th className="text-left px-4 py-2 text-xs font-mono text-muted-foreground uppercase">Action</th>
              <th className="w-12" />
            </tr>
          </thead>
          <tbody>
            {rules.map(rule => (
              <tr key={rule.id} className="border-t border-border hover:bg-secondary/30 transition-colors">
                <td className="px-4 py-2.5 font-mono text-sm">
                  <span className="text-muted-foreground">IF </span>
                  <span className="text-primary">{sensorName(rule.sensorId)}</span>
                  <span className="text-neon-amber"> {rule.operator} </span>
                  <span className="text-foreground">{rule.threshold}</span>
                </td>
                <td className="px-4 py-2.5 font-mono text-sm">
                  <span className="text-muted-foreground">THEN set </span>
                  <span className="text-neon-purple">{actuatorName(rule.actuatorId)}</span>
                  <span className="text-muted-foreground"> to </span>
                  <span className={rule.targetState ? "text-neon-green" : "text-neon-red"}>
                    {rule.targetState ? "ON" : "OFF"}
                  </span>
                </td>
                <td className="px-2">
                  <Button size="icon" variant="ghost" onClick={() => onRemoveRule(rule.id)} className="h-7 w-7 text-muted-foreground hover:text-destructive">
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </td>
              </tr>
            ))}
            {rules.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-6 text-center text-muted-foreground text-sm">No automation rules configured</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
