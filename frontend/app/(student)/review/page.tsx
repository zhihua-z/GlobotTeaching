"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const mockGroups = [
  { subject: "民法", count: 8, color: "bg-blue-500" },
  { subject: "刑法", count: 6, color: "bg-red-500" },
  { subject: "行政法", count: 4, color: "bg-amber-500" },
  { subject: "商经法", count: 3, color: "bg-green-500" },
  { subject: "刑诉法", count: 3, color: "bg-purple-500" },
];

const mockCards = [
  {
    id: 1,
    subject: "民法",
    topic: "物权编 / 善意取得",
    question: "甲将相机借给乙使用，乙擅自以合理价格卖给不知情的丙并交付。丙能否取得相机所有权？",
    options: ["A. 能，丙构成善意取得", "B. 不能，乙无权处分", "C. 能，因丙支付合理价格", "D. 不能，相机为借用物"],
    correctAnswer: "A",
    explanation: "根据《民法典》第311条，受让人善意、合理价格、完成交付，构成善意取得。",
  },
  {
    id: 2,
    subject: "刑法",
    topic: "总则 / 犯罪构成",
    question: "关于犯罪故意中的明知，下列哪一选项是正确的？",
    options: ["A. 明知是确定知道", "B. 明知包括确定知道和应当知道", "C. 明知仅指直接故意中的明知", "D. 明知不包括推定知道"],
    correctAnswer: "B",
    explanation: "明知包括确定知道和应当知道（即知道或应当知道），涵盖直接故意和间接故意。",
  },
];

export default function ReviewPage() {
  const [cardIndex, setCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const totalCards = mockCards.length;
  const currentCard = mockCards[cardIndex];

  const handleRate = (rating: string) => {
    if (cardIndex < totalCards - 1) {
      setCardIndex((i) => i + 1);
      setShowAnswer(false);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      // Complete
    }
  };

  const handleSelectAnswer = (option: string) => {
    if (showResult) return;
    setSelectedAnswer(option);
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
    setShowResult(true);
  };

  const isCorrect = showResult && selectedAnswer === currentCard.correctAnswer;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold mb-2">今日复习</h1>
        <p className="text-muted-foreground">共 {totalCards} 个知识点待复习</p>
      </div>

      {/* Subject groups */}
      <div className="flex flex-wrap gap-2">
        {mockGroups.map((g) => (
          <Badge
            key={g.subject}
            variant="secondary"
            className="text-sm py-1.5 px-3 flex gap-1"
          >
            <span>{g.subject}</span>
            <span className="font-bold">{g.count}</span>
          </Badge>
        ))}
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <Progress value={((cardIndex + 1) / totalCards) * 100} className="flex-1" />
        <span className="text-sm text-muted-foreground">
          {cardIndex + 1} / {totalCards}
        </span>
      </div>

      {/* Current card */}
      <Card>
        <CardContent className="p-6 space-y-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Badge variant="outline">{currentCard.subject}</Badge>
            <span>{currentCard.topic}</span>
          </div>

          <div className="text-lg font-medium">{currentCard.question}</div>

          <div className="space-y-2">
            {currentCard.options.map((opt) => {
              const optLabel = opt.charAt(0);
              const isSelected = selectedAnswer === optLabel;
              let variant: "default" | "outline" | "destructive" | "secondary" = "outline";
              if (showResult && isSelected) {
                variant = isCorrect ? "default" : "destructive";
              } else if (isSelected) {
                variant = "default";
              }
              return (
                <Button
                  key={optLabel}
                  variant={variant}
                  className="w-full justify-start h-auto p-3"
                  onClick={() => handleSelectAnswer(optLabel)}
                  disabled={showResult}
                >
                  {opt}
                </Button>
              );
            })}
          </div>

          {/* Answer section */}
          {showResult && (
            <div className={`p-4 rounded-lg ${isCorrect ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
              <div className="text-sm font-medium mb-1">
                {isCorrect ? "✅ 正确" : "❌ 错误"}
              </div>
              <div className="text-sm text-muted-foreground">{currentCard.explanation}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      {!showResult ? (
        <Button
          className="w-full"
          size="lg"
          onClick={handleShowAnswer}
          disabled={!selectedAnswer}
        >
          显示答案 / 评分
        </Button>
      ) : (
        <div className="grid grid-cols-4 gap-2">
          {["Again", "Hard", "Good", "Easy"].map((rating) => (
            <Button
              key={rating}
              variant="outline"
              onClick={() => handleRate(rating)}
              className="h-16"
            >
              <div>
                <div className="text-sm font-medium">{rating}</div>
                <div className="text-xs text-muted-foreground">
                  {rating === "Again" ? "完全忘了" : rating === "Hard" ? "很困难" : rating === "Good" ? "正常" : "轻松"}
                </div>
              </div>
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}