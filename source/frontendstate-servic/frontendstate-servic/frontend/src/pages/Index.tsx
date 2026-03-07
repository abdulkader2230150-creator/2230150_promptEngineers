import { useMemo } from "react";
import { useMarsData, type SensorData } from "@/hooks/useMarsData";
import { useCriticalTelemetry } from "@/hooks/useCriticalTelemetry";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { SensorCard } from "@/components/dashboard/SensorCard";
import { ActuatorControls } from "@/components/dashboard/ActuatorControls";
import { RuleManager } from "@/components/dashboard/RuleManager";
import { CriticalTelemetry } from "@/components/dashboard/CriticalTelemetry";

const Index = () => {
  const { sensors: criticalSensors } = useCriticalTelemetry();

  const criticalAsSensorData = useMemo<SensorData[]>(() =>
    criticalSensors.map(cs => ({
      id: cs.id,
      name: cs.name,
      value: cs.value,
      unit: cs.unit,
      history: cs.history,
      critical: cs.status === "critical",
    })),
  [criticalSensors]);

  const { sensors, actuators, rules, solTime, setActuatorState, addRule, removeRule } = useMarsData(criticalAsSensorData);

  const allSensors = useMemo<SensorData[]>(() => [
    ...sensors,
    ...criticalAsSensorData,
  ], [sensors, criticalAsSensorData]);

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader solTime={solTime} />
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-8">
        {/* REST Sensors */}
         <section>
           <h2 className="text-sm font-display font-semibold text-muted-foreground uppercase tracking-wider mb-4">
             REST Sensors
           </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {sensors.map(s => (
              <SensorCard key={s.id} sensor={s} />
            ))}
          </div>
        </section>

        <CriticalTelemetry />

        <ActuatorControls actuators={actuators} onSetState={setActuatorState} />

        <RuleManager
          rules={rules}
          sensors={allSensors}
          actuators={actuators}
          onAddRule={addRule}
          onRemoveRule={removeRule}
        />
      </main>
    </div>
  );
};

export default Index;
