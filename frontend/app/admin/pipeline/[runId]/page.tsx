"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { mockApi } from "@/lib/api/mock";
import type { PipelineRun, PipelineStage } from "@/lib/types/api";
import {
  ArrowLeft,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  Play,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

const stageStatusConfig: Record<string, { label: string; color: string; icon: typeof Loader2 }> = {
  pending: { label: "等待中", color: "bg-gray-100 text-gray-600", icon: Clock },
  running: { label: "运行中", color: "bg-blue-100 text-blue-800", icon: Loader2 },
  completed: { label: "已完成", color: "bg-green-100 text-green-800", icon: CheckCircle },
  failed: { label: "失败", color: "bg-red-100 text-red-800", icon: AlertCircle },
};

export default function AdminPipelineRunPage() {
  const params = useParams();
  const [data, setData] = useState<{ run: PipelineRun; stages: PipelineStage[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = params.runId as string;
    mockApi.getPipelineRun(id).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [params.runId]);

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  if (!data) {
    return <div className="text-center py-12 text-muted-foreground">未找到运行记录</div>;
  }

  const { run, stages } = data;
  const runStatusIcon =
    run.status === "running"
      ? Loader2
      : run.status === "completed"
      ? CheckCircle
      : AlertCircle;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/pipeline">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">运行 {run.id}</h1>
            <Badge
              className={
                run.status === "running"
                  ? "bg-blue-100 text-blue-800"
                  : run.status === "completed"
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
              }
            >
              {run.status === "running"
                ? "运行中"
                : run.status === "completed"
                ? "已完成"
                : "失败"}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {run.input_file} · {run.question_count} 题 · 耗时 {run.duration_sec}s
          </p>
        </div>
        {run.status === "failed" && (
          <Button>
            <RefreshCw className="h-4 w-4 mr-2" />
            重试
          </Button>
        )}
      </div>

      {/* Stage Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>处理阶段</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stages.map((stage, idx) => {
              const config = stageStatusConfig[stage.status] || stageStatusConfig.pending;
              const StageIcon = config.icon;
              return (
                <div key={stage.name} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        stage.status === "completed"
                          ? "bg-green-100"
                          : stage.status === "running"
                          ? "bg-blue-100"
                          : stage.status === "failed"
                          ? "bg-red-100"
                          : "bg-gray-100"
                      }`}
                    >
                      <StageIcon
                        className={`h-4 w-4 ${
                          stage.status === "running" ? "animate-spin text-blue-600" : ""
                        } ${
                          stage.status === "completed"
                            ? "text-green-600"
                            : stage.status === "failed"
                            ? "text-red-600"
                            : "text-gray-400"
                        }`}
                      />
                    </div>
                    {idx < stages.length - 1 && (
                      <div className="w-px flex-1 bg-gray-200 my-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-6">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm capitalize">{stage.name}</span>
                      <Badge className={config.color} variant="outline">
                        {config.label}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground space-y-1">
                      {stage.input && <div>输入: {stage.input}</div>}
                      {stage.output && <div>输出: {stage.output}</div>}
                    </div>
                    {stage.logs.length > 0 && (
                      <div className="mt-2 bg-gray-50 rounded p-2 text-xs font-mono space-y-0.5">
                        {stage.logs.map((log, i) => (
                          <div
                            key={i}
                            className={
                              log.startsWith("[ERR]")
                                ? "text-red-600"
                                : log.startsWith("[OK]")
                                ? "text-green-600"
                                : "text-gray-600"
                            }
                          >
                            {log}
                          </div>
                        ))}
                      </div>
                    )}
                    {stage.status === "failed" && (
                      <Button variant="ghost" size="sm" className="mt-2 text-xs">
                        <RefreshCw className="h-3 w-3 mr-1" />
                        重试此阶段
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}