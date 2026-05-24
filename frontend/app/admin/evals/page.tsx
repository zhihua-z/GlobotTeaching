"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { mockApi } from "@/lib/api/mock";
import type { EvalSet, EvalRun, EvalCase } from "@/lib/types/api";
import { Play, ChevronDown, ChevronUp } from "lucide-react";

export default function AdminEvalsPage() {
  const [evalSets, setEvalSets] = useState<EvalSet[]>([]);
  const [evalRuns, setEvalRuns] = useState<EvalRun[]>([]);
  const [failedCases, setFailedCases] = useState<EvalCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedRun, setExpandedRun] = useState<string | null>(null);
  const [tab, setTab] = useState("sets");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      mockApi.getEvalSets(),
      mockApi.getEvalRuns(),
    ]).then(([sets, runs]) => {
      setEvalSets(sets);
      setEvalRuns(runs);
      setLoading(false);
    });
  }, []);

  const handleRunEval = async (setId: string) => {
    const newRun = await mockApi.runEval({ set_id: setId, target: "classify" });
    setEvalRuns((prev) => [newRun, ...prev]);
  };

  const loadFailedCases = async (runId: string) => {
    if (expandedRun === runId) {
      setExpandedRun(null);
      return;
    }
    setExpandedRun(runId);
    const cases = await mockApi.getFailedCases(runId);
    setFailedCases(cases);
  };

  if (loading) {
    return <div className="text-center py-12 text-muted-foreground">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Eval 评测管理</h1>
          <p className="text-sm text-muted-foreground">评测集管理与运行监控</p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="sets">评测集</TabsTrigger>
          <TabsTrigger value="runs">运行记录</TabsTrigger>
        </TabsList>

        <TabsContent value="sets" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {evalSets.map((set) => (
              <Card key={set.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{set.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">目标</span>
                      <Badge variant="outline">{set.target}</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">运行次数</span>
                      <span>{set.run_count}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">创建时间</span>
                      <span>{new Date(set.created_at).toLocaleDateString()}</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => handleRunEval(set.id)}
                    >
                      <Play className="h-4 w-4 mr-2" />
                      运行评测
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="runs" className="mt-4">
          <div className="space-y-4">
            {evalRuns.map((run) => (
              <Card key={run.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Badge
                        variant={run.status === "completed" ? "default" : run.status === "running" ? "secondary" : "destructive"}
                      >
                        {run.status === "completed" ? "已完成" : run.status === "running" ? "运行中" : "失败"}
                      </Badge>
                      <span className="text-sm font-medium">{run.id}</span>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <span className="text-muted-foreground">准确率: {(run.accuracy * 100).toFixed(1)}%</span>
                      <span className="text-muted-foreground">召回率: {(run.recall * 100).toFixed(1)}%</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => loadFailedCases(run.id)}
                      >
                        {expandedRun === run.id ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                        失败用例
                      </Button>
                    </div>
                  </div>
                  {expandedRun === run.id && failedCases.length > 0 && (
                    <div className="mt-4 space-y-2 border-t pt-4">
                      {failedCases.map((c) => (
                        <div key={c.id} className="p-3 bg-red-50 rounded text-sm">
                          <div className="font-medium text-red-700">用例 #{c.id}</div>
                          <div className="mt-1 grid grid-cols-2 gap-2">
                            <div>
                              <span className="text-muted-foreground">输入:</span>
                              <p className="truncate">{c.input}</p>
                            </div>
                            <div>
                              <span className="text-muted-foreground">期望:</span>
                              <p className="truncate">{c.expected}</p>
                            </div>
                            <div className="col-span-2">
                              <span className="text-muted-foreground">实际:</span>
                              <p className="truncate">{c.actual}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}