"use client";

import { useState } from "react";

export default function AnswerBlock({
  answer,
  rubric,
}: {
  answer: string;
  rubric?: Record<string, unknown> | null;
}) {
  const [show, setShow] = useState(false);

  return (
    <div className="p-6">
      <button
        onClick={() => setShow(!show)}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
      >
        <span className={`transform transition-transform ${show ? "rotate-90" : ""}`}>
          ▶
        </span>
        {show ? "隐藏答案" : "显示答案"}
      </button>

      {show && (
        <div className="mt-4 space-y-4">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="text-xs font-medium text-gray-400 uppercase mb-2">答案</h4>
            <p className="text-lg font-medium">{answer}</p>
          </div>

          {rubric && Object.keys(rubric).length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-xs font-medium text-blue-400 uppercase mb-2">评分标准</h4>
              <pre className="text-sm text-blue-800 whitespace-pre-wrap font-sans">
                {JSON.stringify(rubric, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}