"use client";

import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function WeeklyReportPage() {
  const params = useParams();
  const week = params.week as string;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">第 {week} 周报告</h1>
          <p className="text-sm text-muted-foreground">
            本周备考总结与建议
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>本周概览</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">56</div>
              <div className="text-sm text-muted-foreground">本周题量</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">68%</div>
              <div className="text-sm text-muted-foreground">正确率</div>
            </div>
            <div>
              <div className="text-2xl font-bold">12.5h</div>
              <div className="text-sm text-muted-foreground">学习时长</div>
            </div>
            <div>
              <div className="text-2xl font-bold">90%</div>
              <div className="text-sm text-muted-foreground">复习完成率</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>薄弱知识点</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            <li className="text-sm p-2 bg-red-50 rounded-md">
              民法 / 物权编 / 善意取得 — 正确率 40%
            </li>
            <li className="text-sm p-2 bg-red-50 rounded-md">
              刑法 / 分则 / 财产犯罪 — 正确率 45%
            </li>
            <li className="text-sm p-2 bg-amber-50 rounded-md">
              行政法 / 行政许可 — 正确率 55%
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>AI 建议</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>📊 本周正确率较上周下降 5%，建议加强物权编和刑法分则的针对性练习。</p>
          <p>🎯 下周目标：完成行政法一轮复习，正确率稳定在 70% 以上。</p>
          <p>⏰ 建议每日学习时间从 2h 增加至 3h，确保在考前完成全部 8 科复习。</p>
        </CardContent>
      </Card>
    </div>
  );
}