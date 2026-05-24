"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { mockApi } from "@/lib/api/mock";
import type { PipelineRun } from "@/lib/types/api";
import Link from "next/link";
import { Search, Play, RefreshCw, Upload, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

const statusConfig: Record<string, { label: string; color: string; icon: typeof Loader2 }> = {
  running: { label: "运行中", color: "bg-blue-100 text-blue-800", icon: Loader2 },
  completed: { label: "已完成", color: "bg-green-100 text-green-800", icon: CheckCircle },
  failed: { label: "失败", color: "bg-red-100 text-red-800", icon: AlertCircle },
};

export default function AdminPipelinePage() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    mockApi.getPipelineRuns().then((data) => {
      setRuns(data);
      setLoading(false);
    });
  }, []);

  const filtered = search
    ? runs.filter((r) => r.input_file.includes(search) || r.id.includes(search))
    : runs;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">流水线监控</h1>
          <p className="text-sm text-muted-foreground">
            AI 流水线运行状态与历史记录
          </p>
        </div>
        <Button>
          <Upload className="h-4 w-4 mr-2" />
          上传新文件
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索文件名或运行 ID..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="border rounded px-3 py-2 text-sm">
          <option value="">全部状态</option>
          <option value="running">运行中</option>
          <option value="completed">已完成</option>
          <option value="failed">失败</option>
        </select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>运行记录</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">加载中...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">暂无运行记录</div>
          ) : (
            <div className="divide-y">
              {filtered.map((run) => {
                const config = statusConfig[run.status] || statusConfig.completed;
                const StatusIcon = config.icon;
                return (
                  <Link
                    key={run.id}
                    href={`/admin/pipeline/${run.id}`}
                    className="flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors"
                  >
                    <StatusIcon className={`h-5 w-5 shrink-0 ${
                      run.status === "running" ? "animate-spin text-blue-500" :
                      run.status === "completed" ? "text-green-500" : "text-red-500"
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{run.id}</span>
                        <Badge variant="outline" className="text-xs">
                          {run.input_file}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{run.question_count} 题</span>
                        <span>耗时 {run.duration_sec}s</span>
                        <span>{new Date(run.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={config.color}>{config.label}</Badge>
                      {run.status === "running" && (
                        <Button variant="ghost" size="icon" className="shrink-0">
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      )}
                      {run.status === "failed" && (
                        <Button variant="ghost" size="icon" className="shrink-0">
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}