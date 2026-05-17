"use client";

/** Renders the question stem as Markdown (basic rendering, no external deps). */
export default function QuestionStem({ stem }: { stem: string }) {
  return (
    <div className="border rounded-lg p-6 bg-white">
      <div className="prose max-w-none">
        {stem.split("\n").map((line, i) => (
          <p key={i} className="leading-relaxed mb-1">
            {line || "\u00A0"}
          </p>
        ))}
      </div>
    </div>
  );
}