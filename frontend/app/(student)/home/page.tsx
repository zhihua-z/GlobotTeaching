"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  ArrowRight,
  Target,
  TrendingUp,
  Lightbulb,
  BookOpen,
} from "lucide-react";
import Link from "next/link";

const subjects = [
  { name: "民法", progress: 60, color: "bg-blue-500" },
  { name: "刑法", progress: 45, color: "bg-red-500" },
  { name: "行政法", progress: 35, color: "bg-amber-500" },
  { name: "商经法", progress: 28, color: "bg-green-500" },
  { name: "刑诉法", progress: 40, color: "bg-purple-500" },
  { name: "民诉法", progress: 50, color: "bg-pink-500" },
  { name: "理论法", progress: 55, color: "bg-teal-500" },
  { name: "三国法", progress: 20, color: "bg-orange-500" },
];

export default function HomeDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 今日复习卡片 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              今日复习
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-1">12</div>
            <p className="text-sm text-muted-foreground mb-4">
              FSRS 到期知识点
            </p>
            <Link href="/review">
              <Button>
                <ArrowRight className="h-4 w-4 mr-2" />
                开始复习
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* 推荐练习卡片 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              推荐练习
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 mb-4">
              <div className="text-sm font-medium">薄弱点 Top3</div>
              <div className="text-sm text-muted-foreground">
                1. 民法 / 物权编 / 善意取得
              </div>
              <div className="text-sm text-muted-foreground">
                2. 刑法 / 总则 / 犯罪构成
              </div>
              <div className="text-sm text-muted-foreground">
                3. 行政法 / 行政许可
              </div>
            </div>
            <Link href="/practice">
              <Button variant="outline">
                <ArrowRight className="h-4 w-4 mr-2" />
                立即练习
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 知识缺口提示 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-amber-500" />
              AI 建议
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="text-sm p-2 bg-amber-50 rounded-md border border-amber-200">
              💡 建议加强物权编练习，当前掌握度仅 40%
            </div>
            <div className="text-sm p-2 bg-amber-50 rounded-md border border-amber-200">
              💡 刑法分则罪名辨析是常见失分点，推荐专题练习
            </div>
            <div className="text-sm p-2 bg-amber-50 rounded-md border border-amber-200">
              💡 行政诉讼法近期错误率上升，建议复习
            </div>
          </CardContent>
        </Card>

        {/* 本周统计 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              本周统计
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">48</div>
                <div className="text-xs text-muted-foreground">本周题量</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">72%</div>
                <div className="text-xs text-muted-foreground">正确率</div>
              </div>
              <div>
                <div className="text-2xl font-bold">85%</div>
                <div className="text-xs text-muted-foreground">复习完成率</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 8 科进度条 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">8 科备考进度</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {subjects.map((s) => (
            <Link
              key={s.name}
              href="/progress"
              className="flex items-center gap-4 group"
            >
              <span className="w-16 text-sm font-medium shrink-0">
                {s.name}
              </span>
              <div className="flex-1">
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div
                    className={`h-full ${s.color} transition-all`}
                    style={{ width: `${s.progress}%` }}
                  />
                </div>
              </div>
              <span className="w-10 text-sm text-right text-muted-foreground">
                {s.progress}%
              </span>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}