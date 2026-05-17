"use client";

interface Option {
  key: string;
  text: string;
}

export default function OptionsBlock({
  options,
  answer,
  type,
}: {
  options: Record<string, unknown> | unknown;
  answer: string;
  type: string;
}) {
  // Parse options - could be an array of {key, text} or a plain object
  let optionList: Option[] = [];
  if (Array.isArray(options)) {
    optionList = options as Option[];
  }

  if (optionList.length === 0) return null;

  const correctKeys = new Set(
    answer.split(",").map((k) => k.trim().toUpperCase())
  );
  const isMultiple = type === "multiple_choice";

  return (
    <div className="border rounded-lg p-6 bg-white">
      <h3 className="text-sm font-medium text-gray-500 mb-3">选项</h3>
      <div className="space-y-3">
        {optionList.map((opt) => {
          const isCorrect = correctKeys.has(opt.key.toUpperCase());
          return (
            <div
              key={opt.key}
              className={`flex items-start gap-3 p-3 rounded border ${
                isCorrect
                  ? "bg-green-50 border-green-300 ring-1 ring-green-300"
                  : "border-gray-200"
              }`}
            >
              <span
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  isCorrect
                    ? "bg-green-500 text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {opt.key}
              </span>
              <span className="pt-1">{opt.text}</span>
              {isCorrect && (
                <span className="ml-auto text-green-600 text-sm pt-1">
                  {isMultiple ? "✓" : "✓ 正确答案"}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}