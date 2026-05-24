"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { mockApi } from "@/lib/api/mock";
import type { LegalArticle } from "@/lib/types/api";
import { ArrowLeft, Save, Trash2 } from "lucide-react";

const subjects = ["civil", "criminal", "admin", "commercial", "intl", "theory", "crim_proc", "civ_proc"];

const subjectLabels: Record<string, string> = {
  civil: "民法", criminal: "刑法", admin: "行政法", commercial: "商经法",
  intl: "三国法", theory: "理论法", crim_proc: "刑诉", civ_proc: "民诉",
};

export default function AdminLegalArticleEditPage() {
  const params = useParams();
  const router = useRouter();
  const articleId = params.id as string;
  const isNew = articleId === "new";
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    number: "",
    title: "",
    content: "",
    interpretation: "",
    subject: "civil",
    is_high_freq: false,
    effective_date: "",
  });

  useEffect(() => {
    if (!isNew) {
      loadArticle();
    }
  }, [articleId]);

  async function loadArticle() {
    setLoading(true);
    try {
      const data = await mockApi.getLegalArticle(articleId);
      setForm({
        number: data.number,
        title: data.title,
        content: data.content,
        interpretation: data.interpretation,
        subject: data.subject,
        is_high_freq: data.is_high_freq,
        effective_date: data.effective_date,
      });
    } catch {
      // Article not found
    }
    setLoading(false);
  }

  const handleSave = async () => {
    setSaving(true);
    // Mock save
    await new Promise((r) => setTimeout(r, 500));
    setSaving(false);
    router.push("/admin/legal-articles");
  };

  const handleDelete = async () => {
    if (!confirm("确定删除此法条？")) return;
    // Mock delete
    await new Promise((r) => setTimeout(r, 500));
    router.push("/admin/legal-articles");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={() => router.push("/admin/legal-articles")}>
            <ArrowLeft className="w-4 h-4 mr-1" />返回
          </Button>
          <h1 className="text-xl font-bold">{isNew ? "新增法条" : `编辑法条 #${articleId}`}</h1>
        </div>
        <div className="flex gap-2">
          {!isNew && (
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="w-4 h-4 mr-1" />删除
            </Button>
          )}
          <Button onClick={handleSave} disabled={saving}>
            <Save className="w-4 h-4 mr-1" />
            {saving ? "保存中..." : "保存"}
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="number">条文号</Label>
              <Input
                id="number"
                value={form.number}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, number: e.target.value })}
                placeholder="例如: 第1062条"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="subject">所属科目</Label>
              <select
                id="subject"
                value={form.subject}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setForm({ ...form, subject: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg bg-white text-sm"
              >
                {subjects.map((s) => (
                  <option key={s} value={s}>{subjectLabels[s] || s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
              <Label htmlFor="title">标题</Label>
              <Input
                id="title"
                value={form.title}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, title: e.target.value })}
                placeholder="法条标题/名称"
              />
          </div>

            <div className="space-y-2">
              <Label htmlFor="content">条文内容</Label>
              <Textarea
                id="content"
                value={form.content}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setForm({ ...form, content: e.target.value })}
                rows={8}
                placeholder="条文原文..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="interpretation">适用解释</Label>
              <Textarea
                id="interpretation"
                value={form.interpretation}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setForm({ ...form, interpretation: e.target.value })}
                rows={4}
                placeholder="司法解释/适用说明..."
              />
            </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="effective_date">生效日期</Label>
              <Input
                id="effective_date"
                type="date"
                value={form.effective_date}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, effective_date: e.target.value })}
              />
            </div>
            <div className="space-y-2 flex items-end pb-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.is_high_freq}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, is_high_freq: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">标记为高频考点</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}