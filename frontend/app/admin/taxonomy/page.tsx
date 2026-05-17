"use client";

import { useState } from "react";

const FAKAO_SUBJECTS = [
  { code: "civil", name: "民法" },
  { code: "criminal", name: "刑法" },
  { code: "admin", name: "行政法" },
  { code: "commercial", name: "商经法" },
  { code: "intl", name: "三国法" },
  { code: "theory", name: "理论法" },
  { code: "crim_proc", name: "刑诉" },
  { code: "civ_proc", name: "民诉" },
];

const QUESTION_TYPES = [
  { code: "single_choice", label: "单选题", requires_options: true, requires_rubric: false },
  { code: "multiple_choice", label: "多选题", requires_options: true, requires_rubric: false },
  { code: "true_false", label: "判断题", requires_options: false, requires_rubric: false },
  { code: "fill_blank", label: "填空题", requires_options: true, requires_rubric: false },
  { code: "short_answer", label: "简答题", requires_options: false, requires_rubric: true },
  { code: "essay", label: "论述题", requires_options: false, requires_rubric: true },
  { code: "code", label: "编程题", requires_options: true, requires_rubric: true },
  { code: "matching", label: "匹配题", requires_options: true, requires_rubric: false },
  { code: "ordering", label: "排序题", requires_options: true, requires_rubric: false },
];

export default function AdminTaxonomyPage() {
  const [activeTab, setActiveTab] = useState<"subjects" | "types">("subjects");

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">科目 & 题型管理</h1>

      {/* Tabs */}
      <div className="flex border-b mb-6">
        <button
          onClick={() => setActiveTab("subjects")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "subjects"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          科目管理
        </button>
        <button
          onClick={() => setActiveTab("types")}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "types"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          题型管理
        </button>
      </div>

      {/* Tab A: Subjects */}
      {activeTab === "subjects" && (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-700">
              ⚠️ 科目列表固定为法考 8 大科目，仅可编辑描述。如需新增科目，请联系管理员。
            </p>
          </div>

          <div className="border rounded-lg bg-white">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Code</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">名称</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">描述</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 w-20">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {FAKAO_SUBJECTS.map((subject) => (
                  <tr key={subject.code} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{subject.code}</td>
                    <td className="px-4 py-3 font-medium">{subject.name}</td>
                    <td className="px-4 py-3 text-gray-500">法考科目</td>
                    <td className="px-4 py-3 text-right">
                      <button className="text-blue-600 hover:underline text-xs">编辑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-xs text-gray-400 mt-4">
            Curriculum: FAKAO (中国国家统一法律职业资格考试)
          </p>
        </div>
      )}

      {/* Tab B: Question Types */}
      {activeTab === "types" && (
        <div>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-amber-700">
              ⚠️ 题型由后端枚举定义，不允许新增或删除。如需扩展题型，请提交 Alembic migration 修改
              QuestionType 枚举并 seed 此表。
            </p>
          </div>

          <div className="border rounded-lg bg-white">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Code</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">标签</th>
                  <th className="text-center px-4 py-3 font-medium text-gray-500">需要选项</th>
                  <th className="text-center px-4 py-3 font-medium text-gray-500">需要评分</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">描述</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500 w-20">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {QUESTION_TYPES.map((qt) => (
                  <tr key={qt.code} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">{qt.code}</td>
                    <td className="px-4 py-3 font-medium">{qt.label}</td>
                    <td className="px-4 py-3 text-center">
                      {qt.requires_options ? "✅" : "—"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {qt.requires_rubric ? "✅" : "—"}
                    </td>
                    <td className="px-4 py-3 text-gray-500">—</td>
                    <td className="px-4 py-3 text-right">
                      <button className="text-blue-600 hover:underline text-xs">编辑描述</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}