"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RubricBlockProps {
  rubric: Record<string, unknown> | null;
}

function formatRubricValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((v) => `• ${v}`).join("\n");
  }
  return String(value ?? "");
}

export function RubricBlock({ rubric }: RubricBlockProps) {
  if (!rubric || Object.keys(rubric).length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rubric / Marking Criteria</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {Object.entries(rubric).map(([key, value]) => (
          <div key={key}>
            <span className="font-medium text-sm text-muted-foreground capitalize">
              {key.replace(/_/g, " ")}:
            </span>
            <pre className="mt-1 text-sm whitespace-pre-wrap font-sans">
              {formatRubricValue(value)}
            </pre>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}