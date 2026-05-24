"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowLeft, Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";

export default function ImportQuestionsPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [importing, setImporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<{ imported: number; failed: number } | null>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleImport = async () => {
    setImporting(true);
    setProgress(0);
    // Mock import with progress simulation
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((r) => setTimeout(r, 200));
      setProgress(i);
    }
    setResult({ imported: files.length * 45, failed: 2 });
    setImporting(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/questions">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">批量导入题目</h1>
          <p className="text-sm text-muted-foreground">
            支持 .jsonl 和 .md 格式文件
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>上传文件</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary transition-colors cursor-pointer"
          >
            <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
            <p className="text-sm text-muted-foreground mb-2">
              拖拽文件到此处，或点击选择文件
            </p>
            <p className="text-xs text-muted-foreground">
              支持 .jsonl, .md 格式
            </p>
            <input
              type="file"
              multiple
              accept=".jsonl,.md"
              className="hidden"
              onChange={(e) => {
                const selected = Array.from(e.target.files || []);
                setFiles((prev) => [...prev, ...selected]);
              }}
            />
          </div>

          {files.length > 0 && (
            <div className="mt-4 space-y-2">
              <h3 className="text-sm font-medium">已选文件：</h3>
              {files.map((f, i) => (
                <div key={i} className="flex items-center gap-2 text-sm p-2 bg-gray-50 rounded">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span>{f.name}</span>
                  <span className="text-muted-foreground">({(f.size / 1024).toFixed(1)} KB)</span>
                  <button
                    onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                    className="ml-auto text-red-500 hover:text-red-700"
                  >
                    删除
                  </button>
                </div>
              ))}
            </div>
          )}

          {!result && (
            <div className="mt-4">
              <Button onClick={handleImport} disabled={files.length === 0 || importing}>
                {importing ? `导入中 ${progress}%...` : "开始导入"}
              </Button>
            </div>
          )}

          {importing && (
            <div className="mt-4">
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {result && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-4 w-4" />
                <span>成功导入 {result.imported} 题</span>
              </div>
              {result.failed > 0 && (
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <span>{result.failed} 题导入失败</span>
                </div>
              )}
              <Button variant="outline" onClick={() => { setFiles([]); setResult(null); setProgress(0); }}>
                继续导入
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}