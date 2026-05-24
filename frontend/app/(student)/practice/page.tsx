"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import Link from "next/link";

const subjects = ["民法", "刑法", "行政法", "商经法", "刑诉法", "民诉法", "理论法", "三国法"];

const recentSessions = [
  { id: "s1", subject: "民法", count: 10, correct: 7, date: "今天 14:00", status: "completed" },
  { id: "s2", subject: "刑法", count: 5, correct: 3, date: "今天 10:30", status: "in_progress" },
  { id: "s3", subject: "行政法", count: 20, correct: 14, date: "昨天", status: "completed" },
];

export default function PracticePage() {
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [questionCount, setQuestionCount] = useState(10);

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold mb-2">练习</h1>
        <p className="text-muted-foreground">选择科目和范围，开始练习</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>选择科目</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {subjects.map((s) => (
              <Badge
                key={s}
                variant={selectedSubject === s ? "default" : "outline"}
                className="cursor-pointer text-sm py-1.5 px-3"
                onClick={() => setSelectedSubject(s)}
              >
                {s}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>选择范围</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {["推荐（默认）", "薄弱点", "自定义 topic", "真题年份"].map((r) => (
              <Badge
                key={r}
                variant="outline"
                className="cursor-pointer text-sm py-1.5 px-3"
              >
                {r}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>题数 & 题型</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-sm">题数:</span>
            {[10, 20, 50].map((n) => (
              <Badge
                key={n}
                variant={questionCount === n ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => setQuestionCount(n)}
              >
                {n}
              </Badge>
            ))}
            <Input
              type="number"
              className="w-20 h-8"
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm">题型:</span>
            {["单选", "多选", "不定项", "案例分析"].map((t) => (
              <Badge key={t} variant="outline" className="cursor-pointer">
                {t}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Link href={selectedSubject ? `/practice/session-${Date.now()}` : "#"}>
        <Button className="w-full" size="lg" disabled={!selectedSubject}>
          开始练习
        </Button>
      </Link>

      <Card>
        <CardHeader>
          <CardTitle>历史练习记录</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {recentSessions.map((s) => (
              <Link
                key={s.id}
                href={`/practice/${s.id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Badge variant="secondary">{s.subject}</Badge>
                  <span className="text-sm">
                    {s.count} 题 · {s.correct}/{s.count} 正确
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{s.date}</span>
                  <Badge variant={s.status === "in_progress" ? "secondary" : "outline"}>
                    {s.status === "in_progress" ? "进行中" : "已完成"}
                  </Badge>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}