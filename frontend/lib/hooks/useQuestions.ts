import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listQuestions, getQuestion, getQuestionAnalysis, createQuestion, updateQuestion, deleteQuestion } from "@/lib/api/questions";
import type { QuestionResponse, QuestionCreate, QuestionUpdate, QuestionFilters } from "@/src/types/question";

export function useQuestions(filters: QuestionFilters) {
  return useQuery({
    queryKey: ["questions", filters],
    queryFn: () => listQuestions(filters),
    staleTime: 30_000,
  });
}

export function useQuestion(id: string) {
  return useQuery({
    queryKey: ["question", id],
    queryFn: () => getQuestion(id),
    enabled: !!id,
    staleTime: 60_000,
  });
}

export function useQuestionAnalysis(id: string) {
  return useQuery({
    queryKey: ["question", id, "analysis"],
    queryFn: () => getQuestionAnalysis(id),
    enabled: !!id,
    staleTime: 60_000,
  });
}

export function useCreateQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: QuestionCreate) => createQuestion(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
    },
  });
}

export function useUpdateQuestion(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: QuestionUpdate) => updateQuestion(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      queryClient.invalidateQueries({ queryKey: ["question", id] });
    },
  });
}

export function useDeleteQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteQuestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
    },
  });
}