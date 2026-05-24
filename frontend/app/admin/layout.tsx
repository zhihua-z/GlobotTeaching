"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  FileCheck,
  ScrollText,
  GitBranch,
  Terminal,
  BookOpen,
  Tags,
  ChevronLeft,
  Menu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useState } from "react";

const navItems = [
  { href: "/admin", label: "仪表盘", icon: LayoutDashboard },
  { href: "/admin/questions", label: "题库管理", icon: Database },
  { href: "/admin/review", label: "审核队列", icon: FileCheck },
  { href: "/admin/taxonomy", label: "科目管理", icon: Tags },
  { href: "/admin/legal-articles", label: "法条管理", icon: BookOpen },
  { href: "/admin/pipeline", label: "流水线监控", icon: GitBranch },
  { href: "/admin/prompts", label: "Prompt 管理", icon: Terminal },
  { href: "/admin/evals", label: "Eval 评估", icon: ScrollText },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside
        className={cn(
          "bg-gray-950 text-gray-100 flex flex-col transition-all duration-200",
          collapsed ? "w-16" : "w-56"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          {!collapsed && (
            <Link href="/admin" className="text-sm font-bold tracking-tight">
              Globot Admin
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="text-gray-400 hover:text-white"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <Menu className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-gray-800 text-white"
                    : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <Link
            href="/"
            className="text-xs text-gray-500 hover:text-gray-300"
          >
            {collapsed ? "←" : "← 返回前台"}
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 overflow-auto">
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}