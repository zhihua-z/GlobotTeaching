"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import { Search, BookOpen, FileText } from "lucide-react";

const mockArticles = [
  { id: 1, number: "民法典 第311条", title: "善意取得", subject: "民法", summary: "无处分权人将不动产或者动产转让给受让人的，所有权人有权追回；但受让人善意、合理价格、完成登记的除外。", relatedCount: 12, highFreq: true },
  { id: 2, number: "民法典 第563条", title: "合同法定解除", subject: "民法", summary: "因不可抗力致使不能实现合同目的，当事人可以解除合同。", relatedCount: 8, highFreq: true },
  { id: 3, number: "刑法 第264条", title: "盗窃罪", subject: "刑法", summary: "盗窃公私财物数额较大的，处三年以下有期徒刑、拘役或者管制...", relatedCount: 15, highFreq: true },
  { id: 4, number: "刑法 第232条", title: "故意杀人罪", subject: "刑法", summary: "故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑...", relatedCount: 6, highFreq: true },
  { id: 5, number: "行政诉讼法 第25条", title: "原告资格", subject: "行政法", summary: "行政行为的相对人以及其他与行政行为有利害关系的公民、法人或者其他组织，有权提起诉讼。", relatedCount: 4, highFreq: false },
];

const subjects = ["全部", "民法", "刑法", "行政法", "商经法", "刑诉法", "民诉法", "理论法", "三国法"];

export default function LegalArticlesPage() {
  const [selectedSubject, setSelectedSubject] = useState("全部");
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = mockArticles.filter(
    (a) =>
      (selectedSubject === "全部" || a.subject === selectedSubject) &&
      (a.number.includes(searchQuery) || a.title.includes(searchQuery) || a.summary.includes(searchQuery))
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <BookOpen className="h-6 w-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">法条速查</h1>
          <p className="text-sm text-muted-foreground">快速检索法考涉及的核心法条</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索条文号或关键词..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
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
      </div>

      {/* List */}
      <div className="space-y-3">
        {filtered.map((article) => (
          <Link key={article.id} href={`/legal-articles/${article.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <FileText className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{article.number}</span>
                      <Badge variant="secondary">{article.subject}</Badge>
                      {article.highFreq && (
                        <Badge variant="destructive" className="text-xs">高频考点</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">{article.summary}</p>
                    <div className="text-xs text-muted-foreground mt-2">
                      关联 {article.relatedCount} 道题目
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}