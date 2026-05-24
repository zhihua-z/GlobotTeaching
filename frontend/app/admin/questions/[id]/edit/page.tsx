"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import QuestionForm from "@/components/admin/QuestionForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { mockApi } from "@/lib/api/mock";
import type { QuestionDetail } from "@/src/types/question";

export default function EditQuestionPage() {
  const params = useParams();
  const id = params.id as string;
  const [question, setQuestion] = useState<QuestionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    mockApi.getQuestionById(Number(id)).then((q) => {
      setQuestion(q);
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-1" />
          </div>
        </div>
        <Card>
          <CardHeader><Skeleton className="h-6 w-24" /></CardHeader>
          <CardContent><Skeleton className="h-64 w-full" /></CardContent>
        </Card>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/admin/questions">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">题目未找到</h1>
        </div>
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            题目 #{id} 不存在，可能已被删除。
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/questions">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">编辑题目 #{id}</h1>
          <p className="text-sm text-muted-foreground">
            修改题目内容、选项或解析
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>题目信息</CardTitle>
        </CardHeader>
        <CardContent>
          <QuestionForm question={question} />
        </CardContent>
      </Card>
    </div>
  );
}