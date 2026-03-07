interface Props {
  data: number[];
  color?: string;
  critical?: boolean;
}

export function Sparkline({ data, critical }: Props) {
  if (data.length < 2) return <div className="h-8 w-full" />;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const h = 32;
  const w = 120;
  const step = w / (data.length - 1);

  const points = data.map((v, i) => `${i * step},${h - ((v - min) / range) * (h - 4) - 2}`).join(" ");

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-8" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke={critical ? "hsl(var(--neon-red))" : "hsl(var(--primary))"}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}
