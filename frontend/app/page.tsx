'use client';

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-background to-primary/5">
      <div className="text-center space-y-6 max-w-2xl">
        <div className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary mb-4">
          🇨🇳 法考客观题备考平台
        </div>
        <h1 className="text-5xl font-bold tracking-tight">
          Globot Teaching
        </h1>
        <p className="text-xl text-muted-foreground">
          AI 驱动的法考备考助手 · 智能练习 · 个性化复习
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Button size="lg" onClick={() => router.push("/login")}>
            开始使用
          </Button>
          <Button size="lg" variant="outline" onClick={() => window.open("https://github.com/zhihua-z/GlobotTeaching", "_blank")}>
            了解更多
          </Button>
        </div>
        <div className="pt-8 grid grid-cols-3 gap-6 text-sm text-muted-foreground">
          <div className="space-y-1">
            <div className="font-semibold text-foreground">📚 题库</div>
            <div>历年法考真题覆盖</div>
          </div>
          <div className="space-y-1">
            <div className="font-semibold text-foreground">🤖 AI 助教</div>
            <div>苏格拉底式问答</div>
          </div>
          <div className="space-y-1">
            <div className="font-semibold text-foreground">📊 FSRS 复习</div>
            <div>科学间隔重复</div>
          </div>
        </div>
      </div>
    </main>
  );
}
