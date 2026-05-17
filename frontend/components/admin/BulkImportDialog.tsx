"use client";

import { useState } from "react";

export default function BulkImportDialog() {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ created: number; updated: number; failed: number } | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/v1/questions/import", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
      if (data.created > 0 || data.updated > 0) {
        setTimeout(() => {
          setOpen(false);
          setFile(null);
          setResult(null);
        }, 2000);
      }
    } catch {
      alert("导入失败，请重试");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
      >
        批量导入
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
            <h2 className="text-lg font-semibold mb-4">批量导入题目</h2>
            <p className="text-sm text-gray-500 mb-4">
              上传 JSONL 文件，每行一道题目。已存在的 source_origin 将跳过。
            </p>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
              <input
                type="file"
                accept=".jsonl"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                id="bulk-import-file"
              />
              <label htmlFor="bulk-import-file" className="cursor-pointer">
                {file ? (
                  <p className="text-blue-600 font-medium">{file.name}</p>
                ) : (
                  <div>
                    <p className="text-gray-400 mb-1">拖拽文件或点击选择</p>
                    <p className="text-xs text-gray-300">仅支持 .jsonl 格式</p>
                  </div>
                )}
              </label>
            </div>

            {uploading && (
              <div className="mb-4">
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 animate-pulse rounded-full w-2/3" />
                </div>
                <p className="text-xs text-gray-400 mt-1 text-center">导入中...</p>
              </div>
            )}

            {result && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm">
                <p>✅ 新建: {result.created} 题</p>
                <p>🔄 更新: {result.updated} 题</p>
                {result.failed > 0 && <p className="text-red-500">❌ 失败: {result.failed} 题</p>}
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setOpen(false);
                  setFile(null);
                  setResult(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? "导入中..." : "开始导入"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}