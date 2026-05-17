"use client";

import { useState } from "react";

export default function SolutionBlock({ solution }: { solution: string }) {
  const [show, setShow] = useState(false);

  return (
    <div className="p-6 border-t">
      <button
        onClick={() => setShow(!show)}
        className="flex items-center gap-2 text-green-600 hover:text-green-700 font-medium"
      >
        <span className={`transform transition-transform ${show ? "rotate-90" : ""}`}>
          ▶
        </span>
        {show ? "隐藏解析" : "显示解析"}
      </button>

      {show && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-xs font-medium text-green-400 uppercase mb-2">解析</h4>
          <div className="prose prose-sm max-w-none text-gray-700">
            {solution.split("\n").map((line, i) => (
              <p key={i} className="mb-1">
                {line || "\u00A0"}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}