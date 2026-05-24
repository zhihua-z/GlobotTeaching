"use client";

import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";

const mockArticle = {
  id: 1,
  number: "民法典 第311条",
  title: "善意取得",
  subject: "民法",
  content: `无处分权人将不动产或者动产转让给受让人的，所有权人有权追回；但符合下列情形的，受让人取得该不动产或者动产的所有权：

（一）受让人受让该不动产或者动产时是善意；

（二）以合理的价格转让；

（三）转让的不动产或者动产依照法律规定应当登记的已经登记，不需要登记的已经交付给受让人。

受让人依据前款规定取得不动产或者动产的所有权的，原所有权人有权向无处分权人请求损害赔偿。

当事人善意取得其他物权的，参照适用前两款规定。`,
  interpretation: "本条是关于善意取得制度的规定，是物权法中的一项重要制度，旨在保护交易安全。",
  relatedQuestions: [
    { id: "Q123", stem: "关于善意取得的构成要件，下列哪一选项是错误的？" },
    { id: "Q456", stem: "甲将相机借给乙使用，乙擅自卖给丙，丙能否取得所有权？" },
  ],
  highFreq: true,
};

export default function LegalArticleDetailPage() {
  const params = useParams();

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back */}
      <Link href="/legal-articles">
        <Button variant="ghost" size="sm" className="gap-1">
          <ArrowLeft className="h-4 w-4" />
          返回法条列表
        </Button>
      </Link>

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="secondary">{mockArticle.subject}</Badge>
          {mockArticle.highFreq && (
            <Badge variant="destructive" className="text-xs">高频考点</Badge>
          )}
        </div>
        <h1 className="text-2xl font-bold">{mockArticle.number}</h1>
        <p className="text-lg text-muted-foreground">{mockArticle.title}</p>
      </div>

      {/* Content */}
      <Card>
        <CardHeader>
          <CardTitle>条文原文</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="whitespace-pre-line text-sm leading-relaxed">
            {mockArticle.content}
          </div>
        </CardContent>
      </Card>

      {/* Interpretation */}
      <Card>
        <CardHeader>
          <CardTitle>适用解释</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{mockArticle.interpretation}</p>
        </CardContent>
      </Card>

      {/* Related questions */}
      <Card>
        <CardHeader>
          <CardTitle>关联题目</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {mockArticle.relatedQuestions.map((q) => (
            <Link key={q.id} href={`/questions/${q.id}`}>
              <div className="flex items-center gap-2 p-2 rounded-lg hover:bg-secondary/50 transition-colors">
                <span className="text-sm font-mono text-muted-foreground shrink-0">{q.id}</span>
                <span className="text-sm flex-1">{q.stem}</span>
                <ExternalLink className="h-4 w-4 text-muted-foreground shrink-0" />
              </div>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}