"use client";

import type { SimilarQuestion } from "@/types/question";

export default function SimilarList({ similar }: { similar: SimilarQuestion[] }) {
  if (similar.length === 0) return null;

  return (
    <div className="border rounded-lg p-6 bg-white">
      <h3 className="text-sm font-medium text-gray-500 mb-3">相似题目 (Top {similar.length})</h3>
      <div className="space-y-3">
        {similar.map((q) => (
          <a
            key={q.id}
            href={`/questions/${q.id}`}
            className="flex items-start gap-3 p-3 rounded-lg border border-gray-100 hover:border-blue-200 hover:bg-blue-50 transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-800 line-clamp-2 group-hover:text-blue-700">
                {q.stem.slice(0, 120)}{q.stem.length > 120 ? "..." : ""}
              </p>
            </div>
            <div className="flex-shrink-0 flex items-center gap-2">
              <div className="w-16 bg-gray-100 rounded-full h-2">
                <div
                  className="bg-blue-500 rounded-full h-2"
                  style={{ width: `${(q.similarity * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 w-10 text-right">
                {(q.similarity * 100).toFixed(0)}%
              </span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}