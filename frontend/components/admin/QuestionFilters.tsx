"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function QuestionFilters() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [q, setQ] = useState(searchParams.get("q") || "");
  const [curriculum, setCurriculum] = useState(searchParams.get("curriculum") || "");
  const [subject, setSubject] = useState(searchParams.get("subject") || "");
  const [type, setType] = useState(searchParams.get("type") || "");
  const [difficulty, setDifficulty] = useState(searchParams.get("difficulty") || "");

  const applyFilters = () => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (curriculum) params.set("curriculum", curriculum);
    if (subject) params.set("subject", subject);
    if (type) params.set("type", type);
    if (difficulty) params.set("difficulty", difficulty);
    router.push(`/admin/questions?${params.toString()}`);
  };

  const clearFilters = () => {
    setQ("");
    setCurriculum("");
    setSubject("");
    setType("");
    setDifficulty("");
    router.push("/admin/questions");
  };

  const subjectOptions = [
    { value: "civil", label: "民法" },
    { value: "criminal", label: "刑法" },
    { value: "admin", label: "行政法" },
    { value: "commercial", label: "商经法" },
    { value: "intl", label: "三国法" },
    { value: "theory", label: "理论法" },
    { value: "crim_proc", label: "刑诉" },
    { value: "civ_proc", label: "民诉" },
  ];

  const typeOptions = [
    { value: "single_choice", label: "单选题" },
    { value: "multiple_choice", label: "多选题" },
    { value: "true_false", label: "判断题" },
    { value: "fill_blank", label: "填空题" },
    { value: "short_answer", label: "简答题" },
    { value: "essay", label: "论述题" },
  ];

  return (
    <div className="border rounded-lg p-4 bg-white">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs text-gray-500 mb-1">搜索题干</label>
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="输入关键词..."
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            onKeyDown={(e) => e.key === "Enter" && applyFilters()}
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">科目</label>
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">全部科目</option>
            {subjectOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">题型</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">全部题型</option>
            {typeOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">难度</label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 text-sm"
          >
            <option value="">全部难度</option>
            {[1, 2, 3, 4, 5].map((d) => (
              <option key={d} value={d}>
                {"●".repeat(d)}{"○".repeat(5 - d)}
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-2">
          <button
            onClick={applyFilters}
            className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            筛选
          </button>
          <button
            onClick={clearFilters}
            className="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
          >
            清除
          </button>
        </div>
      </div>
    </div>
  );
}