"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, FileCheck, GitBranch, ScrollText } from "lucide-react";

const overviewData = {
  totalQuestions: 1248,
  subjectDistribution: [
    { subject: "民法", count: 320 },
    { subject: "刑法", count: 280 },
    { subject: "行政法", count: 180 },
    { subject: "商经法", count: 150 },
    { subject: "刑诉法", count: 130 },
    { subject: "民诉法", count: 100 },
    { subject: "理论法", count: 55 },
    { subject: "三国法", count: 33 },
  ],
  pendingReview: 124,
  pipelineLast24h: { runs: 3, succeeded: 2, failed: 0, inProgress: 1 },
  lastEvalScore: 87.5,
};

export default function AdminDashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-1">管理后台</h1>
        <p className="text-muted-foreground">Globot 法考系统管理概览</p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Database className="h-6 w-6 text-primary" />
            </div>
            <div>
              <div className="text-2xl font-bold">{overviewData.totalQuestions}</div>
              <div className="text-xs text-muted-foreground">题库总量</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <FileCheck className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{overviewData.pendingReview}</div>
              <div className="text-xs text-muted-foreground">待审核</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <GitBranch className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{overviewData.pipelineLast24h.runs}</div>
              <div className="text-xs text-muted-foreground">流水线 (24h)</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <ScrollText className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{overviewData.lastEvalScore}%</div>
              <div className="text-xs text-muted-foreground">Eval 评分</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Subject distribution */}
        <Card>
          <CardHeader>
            <CardTitle>各科题量分布</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {overviewData.subjectDistribution.map((s) => (
              <div key={s.subject} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{s.subject}</span>
                  <span className="text-muted-foreground">{s.count} 题</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{
                      width: `${(s.count / Math.max(...overviewData.subjectDistribution.map((x) => x.count))) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Pipeline status */}
        <Card>
          <CardHeader>
            <CardTitle>流水线状态（最近 24h）</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">运行次数</span>
              <span className="font-bold">{overviewData.pipelineLast24h.runs}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600">成功</span>
              <span className="font-bold">{overviewData.pipelineLast24h.succeeded}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-red-600">失败</span>
              <span className="font-bold">{overviewData.pipelineLast24h.failed}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-600">进行中</span>
              <span className="font-bold">{overviewData.pipelineLast24h.inProgress}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}