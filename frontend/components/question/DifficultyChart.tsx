"use client";

interface DifficultyChartProps {
  distribution: Record<string, number> | null;
}

export function DifficultyChart({ distribution }: DifficultyChartProps) {
  if (!distribution || Object.keys(distribution).length === 0) {
    return <p className="text-sm text-muted-foreground">No data available</p>;
  }

  const levels = ["1", "2", "3", "4", "5"];
  const maxCount = Math.max(...Object.values(distribution), 1);

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-muted-foreground">
        Difficulty Distribution
      </h4>
      <div className="flex items-end gap-2 h-24">
        {levels.map((level) => {
          const count = distribution[level] ?? 0;
          const height = (count / maxCount) * 100;
          return (
            <div key={level} className="flex-1 flex flex-col items-center gap-1">
              <span className="text-xs font-mono">{count}</span>
              <div
                className="w-full rounded-t bg-primary/80"
                style={{ height: `${Math.max(height, 4)}%` }}
              />
              <span className="text-xs text-muted-foreground">{level}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}