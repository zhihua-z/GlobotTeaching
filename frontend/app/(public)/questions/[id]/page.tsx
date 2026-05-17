import { getQuestion, getQuestionAnalysis } from "@/lib/api/questions";
import QuestionStem from "@/components/question/QuestionStem";
import OptionsBlock from "@/components/question/OptionsBlock";
import AnswerBlock from "@/components/question/AnswerBlock";
import SolutionBlock from "@/components/question/SolutionBlock";
import SimilarList from "@/components/question/SimilarList";
import type { AnalysisResponse } from "@/types/question";

export default async function QuestionDetailPage({ params }: { params: { id: string } }) {
  const questionId = Number(params.id);
  let question;
  let analysis: AnalysisResponse | null = null;

  try {
    [question, analysis] = await Promise.all([
      getQuestion(questionId),
      getQuestionAnalysis(questionId),
    ]);
  } catch {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">题目未找到</h1>
          <p className="text-gray-500">题目 ID: {params.id} 不存在或已被删除。</p>
          <a href="/admin/questions" className="text-blue-600 hover:underline mt-4 inline-block">
            ← 返回题库管理
          </a>
        </div>
      </div>
    );
  }

  const subjectLabels: Record<string, string> = {
    civil: "民法", criminal: "刑法", admin: "行政法", commercial: "商经法",
    intl: "三国法", theory: "理论法", crim_proc: "刑诉", civ_proc: "民诉",
  };

  const typeLabels: Record<string, string> = {
    single_choice: "单选题", multiple_choice: "多选题", true_false: "判断题",
    fill_blank: "填空题", short_answer: "简答题", essay: "论述题",
    code: "编程题", matching: "匹配题", ordering: "排序题",
  };

  const difficultyDots = "●".repeat(question.difficulty || 3) + "○".repeat(5 - (question.difficulty || 3));

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-500 mb-4">
        <a href="/admin/questions" className="hover:text-blue-600">题库</a>
        <span className="mx-2">/</span>
        <span>{subjectLabels[question.subject] || question.subject}</span>
        {question.topic_path?.length > 0 && (
          <>
            <span className="mx-2">/</span>
            <span>{question.topic_path.join(" / ")}</span>
          </>
        )}
      </nav>

      {/* Title row */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <h1 className="text-xl font-bold">Q{question.id}</h1>
        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm font-medium">
          {typeLabels[question.type] || question.type}
        </span>
        <span className="text-sm text-gray-500">难度 {difficultyDots}</span>
        {question.source_year && (
          <span className="text-sm text-gray-400">{question.source_year} 年真题</span>
        )}
        {question.is_indeterminate && (
          <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs">不定项</span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          <QuestionStem stem={question.stem} />
          {question.options && <OptionsBlock options={question.options} answer={question.answer} type={question.type} />}

          {/* Tabs: Answer, Solution, AI Breakdown */}
          <div className="border rounded-lg">
            <AnswerBlock answer={question.answer} rubric={question.rubric} />
            {question.solution && <SolutionBlock solution={question.solution} />}
          </div>

          {/* Similar questions */}
          {analysis?.similar && analysis.similar.length > 0 && (
            <SimilarList similar={analysis.similar} />
          )}
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          {question.source_origin && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-1">来源</h3>
              <p className="text-sm font-mono">{question.source_origin}</p>
            </div>
          )}

          {question.topic_path && question.topic_path.length > 0 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">主题路径</h3>
              <div className="text-sm space-y-1">
                {question.topic_path.map((t, i) => (
                  <div key={i} className="flex items-center gap-1">
                    {i > 0 && <span className="text-gray-300">└</span>}
                    <span>{t}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysis?.stats && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">统计</h3>
              <div className="text-sm space-y-1">
                <p>字数: {analysis.stats.length_chars}</p>
                {analysis.stats.option_count > 0 && <p>选项数: {analysis.stats.option_count}</p>}
                <p>预计阅读: {analysis.stats.estimated_read_time_sec}s</p>
                {analysis.siblings_in_topic > 0 && <p>同主题题目: {analysis.siblings_in_topic}</p>}
              </div>
            </div>
          )}

          {analysis?.difficulty_distribution_in_topic && Object.keys(analysis.difficulty_distribution_in_topic).length > 0 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">同主题难度分布</h3>
              <div className="space-y-1">
                {Object.entries(analysis.difficulty_distribution_in_topic)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([level, count]) => (
                    <div key={level} className="flex items-center gap-2 text-sm">
                      <span className="w-6 text-right">{level}</span>
                      <div className="flex-1 bg-gray-100 rounded h-4">
                        <div
                          className="bg-blue-400 rounded h-4"
                          style={{ width: `${Math.min(100, (count / Math.max(...Object.values(analysis.difficulty_distribution_in_topic))) * 100)}%` }}
                        />
                      </div>
                      <span className="w-6 text-gray-500">{count}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="border rounded-lg p-4 space-y-2">
            <h3 className="text-sm font-medium text-gray-500 mb-2">操作</h3>
            <a
              href={`/admin/questions?edit=${questionId}`}
              className="block w-full text-center px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              编辑
            </a>
            <button className="w-full px-3 py-2 border rounded text-sm hover:bg-gray-50">
              复制题目
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}