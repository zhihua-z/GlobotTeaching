"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Pencil } from "lucide-react";

const subjects = [
  { code: "minfa", name: "民法", progress: 60, current: "物权编 / 善意取得", forecast: "2026.06.20" },
  { code: "xingfa", name: "刑法", progress: 45, current: "总则 / 犯罪构成", forecast: "2026.07.10" },
  { code: "xingzheng", name: "行政法", progress: 35, current: "行政许可", forecast: "2026.07.25" },
  { code: "shangjing", name: "商经法", progress: 28, current: "公司法 / 股东权利", forecast: "2026.08.05" },
  { code: "xingsu", name: "刑诉法", progress: 40, current: "辩护与代理", forecast: "2026.07.15" },
  { code: "minsu", name: "民诉法", progress: 50, current: "管辖制度", forecast: "2026.06.30" },
  { code: "lilun", name: "理论法", progress: 55, current: "法的价值", forecast: "2026.06.15" },
  { code: "sanguo", name: "三国法", progress: 20, current: "国际公法 / 条约法", forecast: "2026.08.20" },
];

export default function ProgressPage() {
  const [dailyHours, setDailyHours] = useState("3.0");
  const [editing, setEditing] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">备考进度</h1>
          <p className="text-muted-foreground">跟踪各科目学习进度和预计完成时间</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">目标考试: 2026-09-XX</span>
          <Badge variant="outline" className="flex items-center gap-1">
            每日可学习: {dailyHours} h
            <button onClick={() => setEditing("daily")}>
              <Pencil className="h-3 w-3" />
            </button>
          </Badge>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>8 科进度详情</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {subjects.map((s) => (
            <div key={s.code} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium w-16">{s.name}</span>
                  <Badge variant="outline" className="text-xs">
                    当前: {s.current}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-muted-foreground">预计完成: {s.forecast}</span>
                  <span className="font-bold">{s.progress}%</span>
                </div>
              </div>
              <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all"
                  style={{ width: `${s.progress}%` }}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>设置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium w-32">每日可学习时间</label>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                className="w-20"
                value={dailyHours}
                onChange={(e) => setDailyHours(e.target.value)}
                step={0.5}
                min={0.5}
                max={12}
              />
              <span className="text-sm text-muted-foreground">小时</span>
            </div>
            <Button size="sm" variant="outline">保存</Button>
          </div>
        </CardContent>
      </Card>

      {/* Forecasting note */}
      <div className="text-sm text-muted-foreground text-center">
        预计完成日期基于当前进度和学习速度估算。完成特定章节后数据会自动更新。
      </div>
    </div>
  );
}