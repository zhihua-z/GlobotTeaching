
"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  ChevronLeft,
  ChevronRight,
  Flag,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";

const mockQuestions = [
  {
    id: "q1",
    stem: "关于民事法律行为的成立与生效，下列哪一表述是正确的？",
    options: [
      { label: "A", text: "民事法律行为的成立与生效是同一概念" },
      { label: "B", text: "民事法律行为自成立时生效，但法律另有规定或者当事人另有约定的除外" },
      { label: "C", text: "附条件的民事法律行为，自条件成就时成立" },
      { label: "D", text: "无效的民事法律行为自始无效，但可追认" },
    ],
    type: "single_choice",
    correctAnswer: "B",
    explanation: "根据《民法典》第136条：民事法律行为自成立时生效，但法律另有规定或者当事人另有约定的除外。",
    citedArticles: ["民法典 第136条"],
  },
  {
    id: "q2",
    stem: "下列哪些情形下，当事人可以解除合同？（多选）",
    options: [
      { label: "A", text: "因不可抗力致使不能实现合同目的" },
      { label: "B", text: "在履行期限届满前，当事人一方明确表示不履行主要债务" },
      { label: "C", text: "当事人一方迟延履行主要债务，经催告后在合理期限内仍未履行" },
      { label: "D", text: "当事人一方轻微违约" },
    ],
    type: "multiple_choice",
    correctAnswer: "ABC",
    explanation: "根据《民法典》第563条：A、B、C三项均为法定解除权的适用情形。D项轻微违约不构成解除合同的条件。",
    citedArticles: ["民法典 第563条"],
  },
];

export default function PracticeSessionPage() {
  const params = useParams();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [showResult, setShowResult] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const question = mockQuestions[currentIndex];
  const progress = ((currentIndex + 1) / mockQuestions.length) * 100;

  const handleSelect = (option: string) => {
    if (submitted) return;
    setSelectedAnswers((prev) => {
      if (question.type === "single_choice") {
        return { ...prev, [question.id]: option };
      }
      // multiple choice: toggle
      const current = prev[question.id] || "";
      const options = current ? current.split(",") : [];
      const idx = options.indexOf(option);
      if (idx >= 0) options.splice(idx, 1);
      else options.push(option);
      return { ...prev, [question.id]: options.sort().join(",") };
    });
  };

  const handleSubmit = () => {
    setSubmitted(true);
    setShowResult(true);
  };

  const isCorrect = submitted && selectedAnswers[question.id] === question.correctAnswer;

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-4">
        <Progress value={progress} className="flex-1" />
        <span className="text-sm text-muted-foreground whitespace-nowrap">
          {currentIndex + 1}/{mockQuestions.length}
        </span>
        <Clock className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">02:14</span>
        <Button variant="outline" size="sm">
          <Flag className="h-4 w-4 mr-1" />
          标记
        </Button>
        <Button variant="outline" size="sm">
          暂停
        </Button>
      </div>

      {/* Question */}
      <Card>
        <CardContent className="p-6 space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <Badge variant="secondary" className="mb-2">
                {question.type === "single_choice" ? "单选题" : "多选题"}
              </Badge>
              <div className="text-lg font-medium">{question.stem}</div>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            {question.options.map((opt) => {
              const isSelected = (selectedAnswers[question.id] || "").includes(opt.label);
              let variant: "default" | "outline" | "destructive" | "secondary" = "outline";
              if (submitted && isSelected) {
                variant = isCorrect ? "default" : "destructive";
              } else if (isSelected) {
                variant = "default";
              }
              return (
                <Button
                  key={opt.label}
                  variant={variant}
                  className="w-full justify-start h-auto p-4 text-left"
                  onClick={() => handleSelect(opt.label)}
                >
                  <span className="w-6 h-6 rounded-full border flex items-center justify-center mr-3 shrink-0 text-sm">
                    {opt.label}
                  </span>
                  <span>{opt.text}</span>
                </Button>
              );
            })}
          </div>

          {/* Result */}
          {showResult && (
            <div className={`p-4 rounded-lg ${isCorrect ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
              <div className="flex items-center gap-2 mb-2">
                {isCorrect ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
                <span className={`font-medium ${isCorrect ? "text-green-700" : "text-red-700"}`}>
                  {isCorrect ? "回答正确！" : "回答错误"}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">{question.explanation}</div>
              {question.citedArticles.length > 0 && (
                <div className="flex gap-2 mt-2">
                  {question.citedArticles.map((a) => (
                    <Badge key={a} variant="outline">{a}</Badge>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => {
            setCurrentIndex((i) => Math.max(0, i - 1));
            setSubmitted(false);
            setShowResult(false);
          }}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-1" /> 上一题
        </Button>
        <div className="flex gap-2">
          {!submitted ? (
            <Button onClick={handleSubmit} disabled={!selectedAnswers[question.id]}>
              提交本题
            </Button>
          ) : currentIndex < mockQuestions.length - 1 ? (
            <Button onClick={() => {
              setCurrentIndex((i) => i + 1);
              setSubmitted(false);
              setShowResult(false);
            }}>
              下一题 <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          ) : (
            <Button>完成练习</Button>
          )}
        </div>
      </div>
    </div>
  );
}