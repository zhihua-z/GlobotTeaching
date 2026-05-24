"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockApi } from "@/lib/api/mock";
import type { PromptTemplate } from "@/lib/types/api";
import { FileText, History, Play, Clock, ChevronRight, Edit3 } from "lucide-react";

const groupLabels: Record<string, string> = {
  chat: "对话助手",
  pipeline: "流水线",
  classify: "分类",
  rubric: "评分",
  report: "报告",
};

export default function AdminPromptsPage() {
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<PromptTemplate | null>(null);
  const [editing, setEditing] = useState(false);
  const [editYaml, setEditYaml] = useState("");

  useEffect(() => {
    mockApi.getPrompts().then((data) => {
      setPrompts(data);
      setLoading(false);
      if (data.length > 0) {
        setSelected(data[0]);
      }
    });
  }, []);

  const groups = Array.from(new Set(prompts.map((p) => p.group)));

  const handleSelect = (p: PromptTemplate) => {
    setSelected(p);
    setEditing(false);
    setEditYaml(p.yaml);
  };

  const handleSave = async () => {
    if (!selected) return;
    // In mock mode, just update local state
    const updated = { ...selected, yaml: editYaml, version: selected.version + 1, updated_at: new Date().toISOString() };
    setSelected(updated);
    setPrompts((prev) => prev.map((p) => (p.name === updated.name ? updated : p)));
    setEditing(false);
  };

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Prompt 模板管理</h1>
          <p className="text-sm text-muted-foreground">
            管理系统 Prompt 模板，支持版本管理与评估
          </p>
        </div>
        <Button variant="outline">
          <History className="h-4 w-4 mr-2" />
          版本历史
        </Button>
      </div>

      <Tabs defaultValue={groups[0] || "chat"}>
        <TabsList>
          {groups.map((g) => (
            <TabsTrigger key={g} value={g}>
              {groupLabels[g] || g}
            </TabsTrigger>
          ))}
        </TabsList>
        {groups.map((g) => (
          <TabsContent key={g} value={g}>
            <div className="flex gap-6">
              {/* Template list */}
              <div className="w-64 shrink-0 space-y-1">
                {prompts
                  .filter((p) => p.group === g)
                  .map((p) => (
                    <button
                      key={p.name}
                      onClick={() => handleSelect(p)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        selected?.name === p.name
                          ? "bg-primary/10 text-primary font-medium"
                          : "hover:bg-muted"
                      }`}
                    >
                      <div className="font-medium">{p.name}</div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        v{p.version} · {new Date(p.updated_at).toLocaleDateString()}
                      </div>
                    </button>
                  ))}
              </div>

              {/* Editor */}
              {selected && (
                <div className="flex-1 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">{selected.name}</h3>
                      <p className="text-xs text-muted-foreground">
                        版本 {selected.version} · 最后更新 {new Date(selected.updated_at).toLocaleString()}
                        {selected.change_note && ` · ${selected.change_note}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditing(!editing)}
                      >
                        <Edit3 className="h-4 w-4 mr-1" />
                        {editing ? "取消" : "编辑"}
                      </Button>
                      <Button size="sm">
                        <Play className="h-4 w-4 mr-1" />
                        运行 Eval
                      </Button>
                    </div>
                  </div>

                  <Card>
                    <CardContent className="p-0">
                      <div className="relative">
                        <textarea
                          className={`w-full min-h-[400px] p-4 font-mono text-sm ${
                            editing ? "bg-white border-2 border-primary/50" : "bg-muted/30"
                          } rounded-lg focus:outline-none resize-y`}
                          value={editing ? editYaml : selected.yaml}
                          onChange={(e) => setEditYaml(e.target.value)}
                          readOnly={!editing}
                          spellCheck={false}
                        />
                      </div>
                    </CardContent>
                  </Card>

                  {editing && (
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => {
                        setEditing(false);
                        setEditYaml(selected.yaml);
                      }}>
                        取消
                      </Button>
                      <Button onClick={handleSave}>保存变更</Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}