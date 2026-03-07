import { Activity } from "lucide-react";

interface Props {
  solTime: { sol: number; time: string };
}

export function DashboardHeader({ solTime }: Props) {
  return (
    <header className="flex items-center justify-between border-b border-border px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
          <Activity className="h-5 w-5 text-primary" />
        </div>
        <h1 className="text-xl font-display font-bold tracking-tight text-foreground">
          MarsOps: Habitat Automation
        </h1>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-neon-green animate-pulse" />
          <span className="text-sm font-mono text-neon-green">System Status: Online</span>
        </div>
        <div className="bg-secondary rounded-md px-3 py-1.5">
          <span className="text-xs text-muted-foreground">Mars Sol Time</span>
          <p className="font-mono text-sm text-foreground font-semibold">
            Sol {solTime.sol} — {solTime.time}
          </p>
        </div>
      </div>
    </header>
  );
}
