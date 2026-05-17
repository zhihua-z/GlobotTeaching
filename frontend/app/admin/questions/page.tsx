import { Suspense } from "react";
import QuestionTable from "@/components/admin/QuestionTable";
import QuestionFilters from "@/components/admin/QuestionFilters";
import BulkImportDialog from "@/components/admin/BulkImportDialog";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default function AdminQuestionsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">题库管理</h1>
        <div className="flex gap-3">
          <Link
            href="/admin/questions/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            + 新建题目
          </Link>
          <BulkImportDialog />
          <a
            href="/api/v1/questions/export?format=jsonl"
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium"
          >
            导出 JSONL
          </a>
        </div>
      </div>

      <Suspense fallback={<div className="border rounded-lg p-4 bg-white animate-pulse h-16" />}>
        <QuestionFilters />
      </Suspense>

      <div className="mt-6">
        <Suspense fallback={<div className="border rounded-lg p-8 animate-pulse space-y-4"><div className="h-12 bg-gray-100 rounded" /><div className="h-12 bg-gray-100 rounded" /></div>}>
          <QuestionTable />
        </Suspense>
      </div>
    </div>
  );
}
