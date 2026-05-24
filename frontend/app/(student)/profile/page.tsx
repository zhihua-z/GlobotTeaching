"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RefreshCw, Download } from "lucide-react";

const mockL1 = "民法物权偏弱（掌握度 45%），刑法稳定（掌握度 72%），建议重点突破物权编和合同编。";

const mockL2 = `## 当前学习状态分析

### 优势领域
- **刑法**: 总则部分掌握良好，犯罪构成理论清晰
- **理论法**: 法的价值与法系比较基础扎实

### 薄弱领域
- **民法**: 物权编善意取得、抵押权实现等概念需要加强
- **行政法**: 行政许可与行政处罚的边界区分不够清晰

### 建议
1. 优先完成民法物权编的专项练习（约 20 题）
2. 每周至少完成 2 次 FSRS 复习巩固已学知识
3. 利用 AI 对话助手对疑难点进行 Socratic 式讨论`;

const mockL3 = [
  { subject: "民法", topics: [
    { name: "物权编 / 善意取得", mastery: 0.35, errors: "典型错误：混淆善意取得与无权处分的法律效果" },
    { name: "物权编 / 抵押权", mastery: 0.50 },
    { name: "合同编 / 合同解除", mastery: 0.85 },
    { name: "债权编 / 不当得利", mastery: 0.60 },
  ]},
  { subject: "刑法", topics: [
    { name: "总则 / 犯罪构成", mastery: 0.82 },
    { name: "总则 / 犯罪中止", mastery: 0.90 },
    { name: "分则 / 财产犯罪", mastery: 0.45, errors: "典型错误：盗窃罪与抢夺罪的区分" },
  ]},
  { subject: "行政法", topics: [
    { name: "行政许可", mastery: 0.40, errors: "典型错误：许可设定权限不清" },
    { name: "行政处罚", mastery: 0.55 },
  ]},
];

const mockEvents = [
  { id: 1, type: "answer", detail: "Q123 回答正确（民法/物权编）", time: "今天 10:23" },
  { id: 2, type: "answer", detail: "Q456 回答错误（民法/善意取得）", time: "今天 10:15" },
  { id: 3, type: "review", detail: "FSRS 复习完成：刑法/犯罪构成（Good）", time: "昨天 20:00" },
  { id: 4, type: "chat", detail: "AI 对话：民法物权编 Socratic 讨论", time: "昨天 19:30" },
];

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("l3");

  const getMasteryColor = (v: number) => {
    if (v >= 0.8) return "bg-green-500";
    if (v >= 0.6) return "bg-blue-500";
    if (v >= 0.4) return "bg-amber-500";
    return "bg-red-500";
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">个人知识图谱</h1>
          <p className="text-sm text-muted-foreground">AI 视角下的知识点掌握情况</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-1">
            <RefreshCw className="h-4 w-4" />
            重建 Profile
          </Button>
          <Button variant="outline" size="sm" className="gap-1">
            <Download className="h-4 w-4" />
            导出 JSON
          </Button>
        </div>
      </div>

      {/* L1 Summary */}
      <Card>
        <CardContent className="p-4">
          <p className="text-sm">{mockL1}</p>
        </CardContent>
      </Card>

      {/* L2 Markdown */}
      <Card>
        <CardHeader>
          <CardTitle>当前状态分析</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <div className="whitespace-pre-line text-sm">{mockL2}</div>
          </div>
        </CardContent>
      </Card>

      {/* L3 Topic Grid */}
      <Card>
        <CardHeader>
          <CardTitle>知识点掌握详情</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-4">
              {mockL3.map((s) => (
                <TabsTrigger key={s.subject} value={s.subject}>{s.subject}</TabsTrigger>
              ))}
            </TabsList>
            {mockL3.map((s) => (
              <TabsContent key={s.subject} value={s.subject} className="space-y-3">
                {s.topics.map((t) => (
                  <div key={t.name} className="p-3 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{t.name}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getMasteryColor(t.mastery)} rounded-full transition-all`}
                            style={{ width: `${t.mastery * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-mono">{(t.mastery * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    {"errors" in t && t.errors && (
                      <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                        {t.errors}
                      </div>
                    )}
                  </div>
                ))}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* L4 Event Stream */}
      <details>
        <summary className="cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground">
          原始事件流（诊断用）
        </summary>
        <div className="mt-3 space-y-2">
          {mockEvents.map((evt) => (
            <div key={evt.id} className="flex items-center gap-3 text-sm p-2 bg-secondary/30 rounded">
              <Badge variant="outline" className="shrink-0">{evt.type}</Badge>
              <span className="flex-1">{evt.detail}</span>
              <span className="text-xs text-muted-foreground shrink-0">{evt.time}</span>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}