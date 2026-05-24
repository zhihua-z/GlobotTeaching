"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { mockApi } from "@/lib/api/mock";
import type { LegalArticle } from "@/lib/types/api";
import Link from "next/link";
import { Plus, Search, BookOpen, Scale } from "lucide-react";

const subjects = ["civil", "criminal", "admin", "commercial", "intl", "theory", "crim_proc", "civ_proc"];

const subjectLabels: Record<string, string> = {
  civil: "民法", criminal: "刑法", admin: "行政法", commercial: "商经法",
  intl: "三国法", theory: "理论法", crim_proc: "刑诉", civ_proc: "民诉",
};

export default function AdminLegalArticlesPage() {
  const [articles, setArticles] = useState<LegalArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [subjectFilter, setSubjectFilter] = useState("");

  useEffect(() => {
    loadArticles();
  }, [search, subjectFilter]);

  async function loadArticles() {
    setLoading(true);
    try {
      const data = await mockApi.getLegalArticles(search || undefined, subjectFilter || undefined);
      setArticles(data);
    } catch {
      setArticles([]);
    }
    setLoading(false);
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Scale className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold">法条管理</h1>
        </div>
        <Link href="/admin/legal-articles/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            新增法条
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="搜索条文号、标题、内容..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button
                variant={subjectFilter === "" ? "default" : "outline"}
                size="sm"
                onClick={() => setSubjectFilter("")}
              >
                全部
              </Button>
              {subjects.map((s) => (
                <Button
                  key={s}
                  variant={subjectFilter === s ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSubjectFilter(s)}
                >
                  {subjectLabels[s] || s}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : articles.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>暂无法条数据</p>
            <Button variant="outline" className="mt-4" onClick={() => loadArticles()}>
              刷新
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {articles.map((article) => (
            <Link key={article.id} href={`/admin/legal-articles/${article.id}/edit`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm text-blue-600 font-bold">
                          {article.number}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          {subjectLabels[article.subject] || article.subject}
                        </Badge>
                        {article.is_high_freq && (
                          <Badge className="bg-amber-100 text-amber-800 text-xs">高频考点</Badge>
                        )}
                      </div>
                      <h3 className="font-medium truncate">{article.title}</h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{article.content}</p>
                    </div>
                    <div className="text-right text-xs text-gray-400 whitespace-nowrap">
                      <div>关联 {article.related_question_ids?.length || 0} 题</div>
                      <div>生效 {article.effective_date}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}