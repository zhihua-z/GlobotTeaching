"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockApi } from "@/lib/api/mock";
import type { QuestionDraft } from "@/lib/types/api";
import Link from "next/link";
import { FileCheck, Search, CheckCircle, XCircle, Clock, AlertTriangle } from "lucide-react";

const statusLabels: Record<string, string> = {
  pending: "待审",
  approved: "已审",
  rejected: "已驳回",
};

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
};

const statusIcons: Record<string, typeof Clock> = {
  pending: Clock,
  approved: CheckCircle,
  rejected: XCircle,
};

export default function AdminReviewPage() {
  const [drafts, setDrafts] = useState<QuestionDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("pending");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    mockApi.getReviewQueue(tab).then((d) => {
      setDrafts(d);
      setLoading(false);
    });
  }, [tab]);

  const filtered = search
    ? drafts.filter((d) => d.stem_preview.includes(search) || d.id.includes(search))
    : drafts;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">审核队列</h1>
          <p className="text-sm text-muted-foreground">
            AI 流水线产出的题目草稿快速审核
          </p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="pending">待审</TabsTrigger>
          <TabsTrigger value="approved">已审</TabsTrigger>
          <TabsTrigger value="rejected">已驳回</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索题号或题干..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="border rounded px-3 py-2 text-sm">
          <option value="">全部科目</option>
          <option value="civil">民法</option>
          <option value="criminal">刑法</option>
          <option value="admin">行政法</option>
        </select>
        <select className="border rounded px-3 py-2 text-sm">
          <option value="">全部置信度</option>
          <option value="0.9">≥ 90%</option>
          <option value="0.8">≥ 80%</option>
          <option value="0.7">≥ 70%</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">加载中...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">暂无审核项</div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="divide-y">
              {filtered.map((draft) => {
                const StatusIcon = statusIcons[draft.status];
                return (
                  <Link
                    key={draft.id}
                    href={`/admin/review/${draft.id}`}
                    className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{draft.id}</span>
                        <Badge variant="outline" className="text-xs">
                          {draft.source_file}
                        </Badge>
                      </div>
                      <p className="text-sm truncate">{draft.stem_preview}</p>
                      <div className="flex items-center gap-3 mt-1">
                        <Badge className={statusColors[draft.status]}>
                          {statusLabels[draft.status]}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {draft.proposed_subject} / {draft.proposed_topic}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          置信度: {(draft.ai_confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <StatusIcon className="h-5 w-5 text-muted-foreground shrink-0" />
                  </Link>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}