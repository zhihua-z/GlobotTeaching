"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Link from "next/link";
import { Search, RotateCcw, CheckCircle2, AlertCircle } from "lucide-react";

const mockMistakes = [
  { id: "Q123", stem: "关于善意取得的构成要件，下列哪一选项是错误的？", subject: "民法", count: 3, lastError: "今天", mastered: false },
  { id: "Q456", stem: "犯罪中止与犯罪未遂的区别在于...", subject: "刑法", count: 2, lastError: "昨天", mastered: false },
  { id: "Q789", stem: "行政许可的设定权限，下列表述正确的是...", subject: "行政法", count: 4, lastError: "3天前", mastered: false },
  { id: "Q234", stem: "关于公司监事会的职权，下列哪一选项是正确的？", subject: "商经法", count: 1, lastError: "5天前", mastered: true },
];

const subjects = ["全部", "民法", "刑法", "行政法", "商经法", "刑诉法", "民诉法", "理论法", "三国法"];

export default function MistakesPage() {
  const [selectedSubject, setSelectedSubject] = useState("全部");
  const [sortBy, setSortBy] = useState("recent");

  const filtered = mockMistakes.filter(
    (m) => selectedSubject === "全部" || m.subject === selectedSubject
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">错题本</h1>
        <p className="text-muted-foreground">回顾错题，巩固薄弱知识点</p>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex flex-wrap gap-1">
            {subjects.map((s) => (
              <Badge
                key={s}
                variant={selectedSubject === s ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => setSelectedSubject(s)}
              >
                {s}
              </Badge>
            ))}
          </div>
          <div className="flex items-center gap-2 ml-auto">
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="排序" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">最近错误</SelectItem>
                <SelectItem value="count">错误次数</SelectItem>
              </SelectContent>
            </Select>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="搜索题号..." className="pl-8 w-48" />
            </div>
          </div>
        </div>
      </Card>

      {/* List */}
      <div className="space-y-2">
        {filtered.map((m) => (
          <Card key={m.id} className="p-4">
            <div className="flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="secondary" className="shrink-0">{m.subject}</Badge>
                  <span className="text-sm font-mono text-muted-foreground">{m.id}</span>
                  {!m.mastered && <AlertCircle className="h-4 w-4 text-red-500" />}
                  {m.mastered && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                </div>
                <p className="text-sm truncate">{m.stem}</p>
                <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                  <span>错误 {m.count} 次</span>
                  <span>最近: {m.lastError}</span>
                </div>
              </div>
              <div className="flex flex-col gap-1 shrink-0">
                <Link href={`/practice/session-retry-${m.id}`}>
                  <Button size="sm" variant="outline" className="gap-1">
                    <RotateCcw className="h-3 w-3" />
                    再做一次
                  </Button>
                </Link>
                <Link href={`/questions/${m.id}`}>
                  <Button size="sm" variant="ghost">查看解析</Button>
                </Link>
                {!m.mastered && (
                  <Button size="sm" variant="ghost" className="text-green-600">
                    标记已掌握
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}