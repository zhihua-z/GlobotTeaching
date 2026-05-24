"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import {
  TrendingUp,
  Flame,
  Target,
  BookOpen,
  AlertTriangle,
} from "lucide-react";

const heatmapData = [
  { subject: "民法", topics: [{ name: "物权编", level: 3 }, { name: "债权编", level: 2 }, { name: "合同编", level: 1 }] },
  { subject: "刑法", topics: [{ name: "总则", level: 2 }, { name: "分则", level: 1 }, { name: "罪名", level: 0 }] },
  { subject: "行政法", topics: [{ name: "许可", level: 1 }, { name: "处罚", level: 0 }, { name: "诉讼", level: 1 }] },
];

const weakPoints = [
  { subject: "民法", topic: "物权编 / 善意取得", score: 0.35 },
  { subject: "刑法", topic: "分则 / 财产犯罪", score: 0.42 },
  { subject: "行政法", topic: "行政许可设定", score: 0.48 },
  { subject: "刑诉法", topic: "证据规则", score: 0.45 },
  { subject: "商经法", topic: "公司治理结构", score: 0.50 },
];

const weeklyTrend = [32, 45, 38, 52];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">自学看板</h1>

      {/* Row 1: Key metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">486</div>
            <div className="text-xs text-muted-foreground mt-1">倒计时 (天)</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold flex items-center justify-center gap-1">
              <Flame className="h-5 w-5 text-orange-500" />
              7
            </div>
            <div className="text-xs text-muted-foreground mt-1">连续学习</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold">48</div>
            <div className="text-xs text-muted-foreground mt-1">本周题量</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">72%</div>
            <div className="text-xs text-muted-foreground mt-1">本周正确率</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">85%</div>
            <div className="text-xs text-muted-foreground mt-1">复习完成率</div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            知识点掌握热力图
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {heatmapData.map((s) => (
              <div key={s.subject}>
                <div className="text-sm font-medium mb-2">{s.subject}</div>
                <div className="flex flex-wrap gap-2">
                  {s.topics.map((t) => (
                    <div
                      key={t.name}
                      className={`px-3 py-1.5 rounded-md text-sm ${
                        t.level >= 3
                          ? "bg-green-100 text-green-800 border border-green-300"
                          : t.level >= 2
                            ? "bg-blue-100 text-blue-800 border border-blue-300"
                            : t.level >= 1
                              ? "bg-amber-100 text-amber-800 border border-amber-300"
                              : "bg-red-100 text-red-800 border border-red-300"
                      }`}
                    >
                      {t.name}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Row 3: Weak points + Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              薄弱点 Top5
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {weakPoints.map((w, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{w.subject}</Badge>
                  <span className="text-sm">{w.topic}</span>
                </div>
                <span className="text-sm font-mono text-red-600">
                  {(w.score * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              最近 4 周题量趋势
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-around h-32">
              {weeklyTrend.map((v, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <span className="text-xs font-medium">{v}</span>
                  <div
                    className="w-8 bg-primary rounded-t-md transition-all"
                    style={{ height: `${(v / 60) * 100}%` }}
                  />
                  <span className="text-xs text-muted-foreground">W{-3 + i}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 4: Reports link */}
      <Card>
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <span className="font-medium">周报</span>
          </div>
          <Link href="/dashboard/reports/latest">
            <Badge variant="secondary" className="cursor-pointer">
              查看最新周报 →
            </Badge>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}