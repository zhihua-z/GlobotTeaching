"use client";

import QuestionForm from "@/components/admin/QuestionForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NewQuestionPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/questions">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">新建题目</h1>
          <p className="text-sm text-muted-foreground">
            手动录入一道新题目
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>题目信息</CardTitle>
        </CardHeader>
        <CardContent>
          <QuestionForm />
        </CardContent>
      </Card>
    </div>
  );
}