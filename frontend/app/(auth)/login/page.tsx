"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { GraduationCap } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import Link from "next/link";

export default function LoginPage() {
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Mock login
    await new Promise((r) => setTimeout(r, 800));
    if (email === "zhihua@globot.com" && password === "123456") {
      // Set mock session cookies so middleware doesn't redirect
      document.cookie = "session_token=mock-session-token; path=/; max-age=86400";
      document.cookie = "user_role=student; path=/; max-age=86400";
      toast({ title: "登录成功", description: "欢迎回到 Globot 法考" });
      // Use full page navigation so middleware re-checks cookies
      window.location.href = "/home";
    } else {
      toast({
        title: "登录失败",
        description: "邮箱或密码错误",
        variant: "destructive",
      });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <GraduationCap className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-2xl">Globot 法考</CardTitle>
          <CardDescription>登录你的备考账号</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                type="email"
                placeholder="zhihua@globot.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="flex items-center justify-between text-sm">
              <Label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded" />
                记住我
              </Label>
              <Link href="#" className="text-primary hover:underline">
                忘记密码
              </Link>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "登录中..." : "登录"}
            </Button>
          </form>
          <p className="text-center text-xs text-muted-foreground mt-4">
            演示账号: zhihua@globot.com / 123456
          </p>
        </CardContent>
      </Card>
    </div>
  );
}