"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { mockApi } from "@/lib/api/mock";
import type { QuestionDraft } from "@/lib/types/api";
import { CheckCircle, XCircle, ArrowLeft, ArrowRight, AlertTriangle } from "lucide-react";

export default function ReviewDraftPage() {
  const params = useParams();
  const router = useRouter();
  const draftId = params.draftId as string;
  const [draft, setDraft] = useState<QuestionDraft | null>(null);
  const [loading, setLoading] = useState(true);

  const loadDraft = useCallback(async () => {
    setLoading(true);
    try {
      const data = await mockApi.getDraft(draftId);
      setDraft(data);
    } catch {
      setDraft(null);
    }
    setLoading(false);
  }, [draftId]);

  useEffect(() => {
    loadDraft();
  }, [loadDraft]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      switch (e.key.toLowerCase()) {
        case "a":
          handleApprove();
          break;
        case "r":
          handleReject();
          break;
        case "j":
          router.push(`/admin/review/${Number(draftId) - 1}`);
          break;
        case "k":
          router.push(`/admin/review/${Number(draftId) + 1}`);
          break;
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [draftId, draft]);

  const handleApprove = async () => {
    if (!draft) return;
    await mockApi.approveDraft(draft.id);
    router.push("/admin/review");
  };

  const handleReject = async () => {
    if (!draft) return;
    await mockApi.rejectDraft(draft.id);
    router.push("/admin/review");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">审核草稿未找到</h1>
        <p className="text-gray-500">Draft ID: {draftId} 不存在。</p>
        <Button variant="outline" onClick={() => router.push("/admin/review")} className="mt-4">
          ← 返回审核队列
        </Button>
      </div>
    );
  }

  const proposedData = draft.proposed_data as Record<string, unknown>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={() => router.push("/admin/review")}>
            <ArrowLeft className="w-4 h-4 mr-1" />
            返回
          </Button>
          <h1 className="text-xl font-bold">审核草稿 #{draft.id}</h1>
          <Badge className={
            draft.status === "approved" ? "bg-green-100 text-green-800" :
            draft.status === "rejected" ? "bg-red-100 text-red-800" :
            "bg-yellow-100 text-yellow-800"
          }>
            {draft.status === "approved" ? "已通过" : draft.status === "rejected" ? "已驳回" : "待审"}
          </Badge>
          <Badge className="bg-blue-100 text-blue-800">
            置信度: {Math.round(draft.ai_confidence * 100)}%
          </Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push(`/admin/review/${Number(draftId) - 1}`)}>
            <ArrowLeft className="w-4 h-4 mr-1" />上一题 (K)
          </Button>
          <Button variant="outline" onClick={() => router.push(`/admin/review/${Number(draftId) + 1}`)}>
            下一题 (J) <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Original Preview */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">原始数据预览</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <div className="mb-4">
                <span className="text-gray-500 text-xs">来源文件: </span>
                <code className="text-xs bg-gray-100 px-1">{draft.source_file}</code>
              </div>
              <p className="text-gray-900 whitespace-pre-wrap font-mono text-sm bg-gray-50 p-3 rounded">
                {draft.stem_preview}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Right: AI Proposed Data */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-500">AI 提议数据</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs text-gray-500">科目</label>
              <p className="font-medium">{draft.proposed_subject}</p>
            </div>
            <div>
              <label className="text-xs text-gray-500">主题</label>
              <p className="font-medium">{draft.proposed_topic}</p>
            </div>
            <div>
              <label className="text-xs text-gray-500">题型</label>
              <p className="font-medium">{String(proposedData.type || "未知")}</p>
            </div>
            <div>
              <label className="text-xs text-gray-500">答案</label>
              <p className="font-medium">{String(proposedData.answer || "未知")}</p>
            </div>
            {Boolean(proposedData.rubric) && (
              <div>
                <label className="text-xs text-gray-500">评分标准</label>
                <pre className="text-xs bg-gray-50 p-2 rounded mt-1 whitespace-pre-wrap">
                  {JSON.stringify(proposedData.rubric, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Action buttons */}
      {draft.status === "pending" && (
        <div className="flex justify-center gap-4 mt-8">
          <Button onClick={handleApprove} className="bg-green-600 hover:bg-green-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            通过 (A)
          </Button>
          <Button onClick={handleReject} variant="destructive">
            <XCircle className="w-4 h-4 mr-2" />
            驳回 (R)
          </Button>
        </div>
      )}

      <div className="mt-4 text-center text-xs text-gray-400">
        快捷键: J/K 切换题目 · A 通过 · R 驳回
      </div>
    </div>
  );
}