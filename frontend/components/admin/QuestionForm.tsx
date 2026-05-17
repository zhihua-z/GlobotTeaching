"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  QuestionType,
  QuestionCreate,
  QuestionUpdate,
  QuestionDetail,
  QuestionTypeMeta,
} from "@/src/types/question";
import { createQuestion, updateQuestion } from "@/lib/api/questions";

interface QuestionFormProps {
  question?: QuestionDetail; // undefined = create mode
}

export default function QuestionForm({ question }: QuestionFormProps) {
  const router = useRouter();
  const isEdit = !!question;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<QuestionCreate>({
    curriculum: "FAKAO",
    subject: "",
    topic_path: [],
    difficulty: 3,
    type: "single_choice",
    stem: "",
    options: null,
    answer: "",
    rubric: null,
    solution: null,
    source_origin: null,
    source_year: null,
    is_indeterminate: false,
    cited_articles: [],
  });

  useEffect(() => {
    if (question) {
      setForm({
        curriculum: question.curriculum,
        subject: question.subject,
        topic_path: question.topic_path,
        difficulty: question.difficulty,
        type: question.type,
        stem: question.stem,
        options: question.options as Record<string, unknown> | null,
        answer: question.answer,
        rubric: question.rubric as Record<string, unknown> | null,
        solution: question.solution,
        source_origin: question.source_origin,
        source_year: question.source_year,
        is_indeterminate: question.is_indeterminate,
        cited_articles: question.cited_articles,
      });
    }
  }, [question]);

  const handleChange = (
    field: keyof QuestionCreate,
    value: unknown
  ) => {
    setForm((prev: QuestionCreate) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isEdit && question) {
        const updateData: QuestionUpdate = {};
        (Object.keys(form) as (keyof QuestionCreate)[]).forEach((key) => {
          const v = form[key];
          if (v !== undefined && v !== null) {
            (updateData as Record<string, unknown>)[key] = v;
          }
        });
        await updateQuestion(String(question.id), updateData);
      } else {
        await createQuestion(form);
      }
      router.push("/admin/questions");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setLoading(false);
    }
  };

  const renderOptionsEditor = () => {
    const options = (form.options as unknown as { key: string; text: string }[]) || [];
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium">选项</label>
        {options.map((opt: { key: string; text: string }, i: number) => (
          <div key={i} className="flex gap-2">
            <input
              className="w-12 px-2 py-1 border rounded"
              placeholder="Key"
              value={opt.key}
              onChange={(e) => {
                const newOpts = [...options];
                newOpts[i] = { ...newOpts[i], key: e.target.value };
                handleChange("options", newOpts);
              }}
            />
            <input
              className="flex-1 px-2 py-1 border rounded"
              placeholder="Text"
              value={opt.text}
              onChange={(e) => {
                const newOpts = [...options];
                newOpts[i] = { ...newOpts[i], text: e.target.value };
                handleChange("options", newOpts);
              }}
            />
            <button
              type="button"
              onClick={() => {
                const newOpts = options.filter(
                  (_: { key: string; text: string }, j: number) => j !== i
                );
                handleChange("options", newOpts);
              }}
              className="px-2 py-1 text-red-600 hover:bg-red-50 rounded"
            >
              删除
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() =>
            handleChange("options", [
              ...options,
              { key: "", text: "" },
            ])
          }
          className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
        >
          + 添加选项
        </button>
      </div>
    );
  };

  const renderRubricEditor = () => {
    const rubric = form.rubric as {
      max_marks?: number;
      criteria?: string[];
    } | null;
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium">评分细则</label>
        <input
          className="w-full px-2 py-1 border rounded"
          placeholder="满分"
          type="number"
          value={rubric?.max_marks ?? ""}
          onChange={(e) =>
            handleChange("rubric", {
              ...rubric,
              max_marks: parseInt(e.target.value) || 0,
            })
          }
        />
        {(rubric?.criteria || []).map((c: string, i: number) => (
          <div key={i} className="flex gap-2">
            <input
              className="flex-1 px-2 py-1 border rounded"
              placeholder={`评分标准 ${i + 1}`}
              value={c}
              onChange={(e) => {
                const newCriteria = [...(rubric?.criteria || [])];
                newCriteria[i] = e.target.value;
                handleChange("rubric", {
                  ...rubric,
                  criteria: newCriteria,
                });
              }}
            />
            <button
              type="button"
              onClick={() => {
                const newCriteria = (rubric?.criteria || []).filter(
                  (_: string, j: number) => j !== i
                );
                handleChange("rubric", { ...rubric, criteria: newCriteria });
              }}
              className="px-2 py-1 text-red-600 hover:bg-red-50 rounded"
            >
              删除
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() =>
            handleChange("rubric", {
              ...rubric,
              criteria: [...(rubric?.criteria || []), ""],
            })
          }
          className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
        >
          + 添加评分标准
        </button>
      </div>
    );
  };

  const needsOptions = ["single_choice", "multiple_choice", "matching", "ordering"].includes(form.type);
  const needsRubric = ["short_answer", "essay", "code"].includes(form.type);

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-6">
      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">课程</label>
          <input
            className="w-full px-3 py-2 border rounded bg-gray-50"
            value={form.curriculum}
            readOnly
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">科目</label>
          <input
            className="w-full px-3 py-2 border rounded"
            placeholder="如 civil"
            value={form.subject}
            onChange={(e) => handleChange("subject", e.target.value)}
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">题型</label>
        <select
          className="w-full px-3 py-2 border rounded"
          value={form.type}
          onChange={(e) => handleChange("type", e.target.value)}
        >
          <option value="single_choice">单选</option>
          <option value="multiple_choice">多选</option>
          <option value="true_false">判断</option>
          <option value="fill_blank">填空</option>
          <option value="short_answer">简答</option>
          <option value="essay">论述</option>
          <option value="code">编程</option>
          <option value="matching">匹配</option>
          <option value="ordering">排序</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">难度 (1-5)</label>
        <input
          className="w-full px-3 py-2 border rounded"
          type="number"
          min={1}
          max={5}
          value={form.difficulty ?? 3}
          onChange={(e) => handleChange("difficulty", parseInt(e.target.value) || 3)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">题干 (Markdown)</label>
        <textarea
          className="w-full px-3 py-2 border rounded min-h-[120px] font-mono text-sm"
          value={form.stem}
          onChange={(e) => handleChange("stem", e.target.value)}
          required
        />
      </div>

      {needsOptions && renderOptionsEditor()}

      <div>
        <label className="block text-sm font-medium mb-1">答案</label>
        <textarea
          className="w-full px-3 py-2 border rounded min-h-[60px] font-mono text-sm"
          value={form.answer || ""}
          onChange={(e) => handleChange("answer", e.target.value)}
        />
      </div>

      {needsRubric && renderRubricEditor()}

      <div>
        <label className="block text-sm font-medium mb-1">解析 (Markdown)</label>
        <textarea
          className="w-full px-3 py-2 border rounded min-h-[80px] font-mono text-sm"
          value={form.solution || ""}
          onChange={(e) => handleChange("solution", e.target.value)}
        />
      </div>

      <div className="flex gap-4 items-center">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-1">来源</label>
          <input
            className="w-full px-3 py-2 border rounded"
            placeholder="如 FAKAO-2022-卷一-第3题"
            value={form.source_origin || ""}
            onChange={(e) => handleChange("source_origin", e.target.value)}
          />
        </div>
        <div className="w-24">
          <label className="block text-sm font-medium mb-1">年份</label>
          <input
            className="w-full px-3 py-2 border rounded"
            type="number"
            placeholder="2022"
            value={form.source_year || ""}
            onChange={(e) => handleChange("source_year", parseInt(e.target.value) || null)}
          />
        </div>
      </div>

      <div className="flex gap-4">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={form.is_indeterminate || false}
            onChange={(e) => handleChange("is_indeterminate", e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">不定项选择</span>
        </label>
      </div>

      <div className="flex gap-4 pt-4 border-t">
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "保存中..." : isEdit ? "更新题目" : "创建题目"}
        </button>
        <button
          type="button"
          onClick={() => router.push("/admin/questions")}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          取消
        </button>
      </div>
    </form>
  );
}