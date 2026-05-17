"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { listQuestions, deleteQuestion } from "@/lib/api/questions";
import type { QuestionListItem } from "@/types/question";

export default function QuestionTable() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [questions, setQuestions] = useState<QuestionListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(Number(searchParams.get("page")) || 1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const pageSize = 20;

  const typeLabels: Record<string, string> = {
    single_choice: "单选", multiple_choice: "多选", true_false: "判断",
    fill_blank: "填空", short_answer: "简答", essay: "论述",
    code: "编程", matching: "匹配", ordering: "排序",
  };

  const subjectLabels: Record<string, string> = {
    civil: "民法", criminal: "刑法", admin: "行政法", commercial: "商经法",
    intl: "三国法", theory: "理论法", crim_proc: "刑诉", civ_proc: "民诉",
  };

  const fetchQuestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters: Record<string, string> = {};
      const q = searchParams.get("q");
      const curriculum = searchParams.get("curriculum");
      const subject = searchParams.get("subject");
      const type = searchParams.get("type");
      const difficulty = searchParams.get("difficulty");

      if (q) filters.q = q;
      if (curriculum) filters.curriculum = curriculum;
      if (subject) filters.subject = subject;
      if (type) filters.type = type;
      if (difficulty) filters.difficulty = difficulty;

      const result = await listQuestions({
        ...filters,
        page,
        page_size: pageSize,
        sort: "-created_at",
      });
      setQuestions(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [searchParams, page]);

  const totalPages = Math.ceil(total / pageSize);

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这道题目吗？此操作不可撤销。")) return;
    try {
      await deleteQuestion(id);
      setQuestions((prev) => prev.filter((q) => q.id !== id));
      setTotal((prev) => prev - 1);
    } catch {
      alert("删除失败，请重试");
    }
  };

  if (loading) {
    return (
      <div className="border rounded-lg p-8">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border rounded-lg p-8 text-center text-red-500">
        <p>加载失败: {error}</p>
        <button onClick={fetchQuestions} className="mt-2 text-blue-600 hover:underline">
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="border rounded-lg bg-white">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500 w-16">#</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">题干</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500 w-20">科目</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500 w-16">题型</th>
              <th className="text-center px-4 py-3 font-medium text-gray-500 w-16">难度</th>
              <th className="text-left px-4 py-3 font-medium text-gray-500 w-24">来源</th>
              <th className="text-right px-4 py-3 font-medium text-gray-500 w-20">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {questions.map((q) => (
              <tr
                key={q.id}
                className="hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => router.push(`/questions/${q.id}`)}
              >
                <td className="px-4 py-3 text-gray-400 font-mono text-xs">{q.id}</td>
                <td className="px-4 py-3">
                  <p className="line-clamp-1 text-gray-800">
                    {q.stem.slice(0, 100)}{q.stem.length > 100 ? "..." : ""}
                  </p>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs text-gray-500">
                    {subjectLabels[q.subject] || q.subject}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-xs">
                    {typeLabels[q.type] || q.type}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  {"●".repeat(q.difficulty || 0)}{"○".repeat(5 - (q.difficulty || 0))}
                </td>
                <td className="px-4 py-3 text-xs text-gray-400">
                  {q.source_year || q.source_origin?.slice(0, 15)}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(q.id);
                    }}
                    className="text-red-500 hover:text-red-700 text-xs"
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
            {questions.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-gray-400">
                  暂无题目数据
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t">
          <span className="text-sm text-gray-500">共 {total} 条</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              上一页
            </button>
            <span className="px-3 py-1 text-sm text-gray-600">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      )}
    </div>
  );
}