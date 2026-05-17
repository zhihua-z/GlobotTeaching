"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";

interface QuestionTypeMeta {
  code: string;
  label_en: string;
  label_zh: string;
  requires_options: boolean;
  requires_rubric: boolean;
  description: string;
}

export function useQuestionTypes() {
  return useQuery<QuestionTypeMeta[]>({
    queryKey: ["question-types"],
    queryFn: () => apiFetch<QuestionTypeMeta[]>("/api/v1/question-types"),
    staleTime: 5 * 60 * 1000,
  });
}
