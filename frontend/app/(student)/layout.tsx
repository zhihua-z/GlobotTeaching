"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Home,
  MessageSquare,
  Edit3,
  RefreshCw,
  AlertTriangle,
  BarChart3,
  BookOpen,
  User,
  LayoutDashboard,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
} from "lucide-react";

const navItems = [
  { href: "/home", label: "首页看板", icon: Home },
  { href: "/chat", label: "AI 对话", icon: MessageSquare },
  { href: "/practice", label: "练习", icon: Edit3 },
  { href: "/review", label: "今日复习", icon: RefreshCw },
  { href: "/mistakes", label: "错题本", icon: AlertTriangle },
  { href: "/progress", label: "备考进度", icon: BarChart3 },
  { href: "/dashboard", label: "自学看板", icon: LayoutDashboard },
  { href: "/legal-articles", label: "法条速查", icon: BookOpen },
  { href: "/profile", label: "知识图谱", icon: User },
];

export default function StudentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center px-4 gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="shrink-0"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
            <GraduationCap className="h-6 w-6 text-primary" />
            <span>Globot 法考</span>
          </Link>
          <div className="flex-1" />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>距 2026.9.XX 法考还剩</span>
            <span className="font-bold text-primary">132</span>
            <span>天</span>
            <span className="ml-2">🔥 streak 5</span>
          </div>
        </div>
      </header>
      <div className="flex">
        {/* Sidebar */}
        <aside
          className={cn(
            "border-r bg-muted/30 transition-all duration-200",
            sidebarCollapsed ? "w-16" : "w-56"
          )}
        >
          <nav className="flex flex-col gap-1 p-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href ||
                (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start gap-3",
                      sidebarCollapsed && "justify-center px-2"
                    )}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {!sidebarCollapsed && <span>{item.label}</span>}
                  </Button>
                </Link>
              );
            })}
          </nav>
        </aside>
        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}