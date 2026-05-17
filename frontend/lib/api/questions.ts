import { apiFetch } from "./client";
import type {
  QuestionDetail,
  QuestionListResponse,
  QuestionCreate,
  QuestionUpdate,
  AnalysisResponse,
  SimilarQuestion,
  QuestionFilters,
} from "@/types/question";

function buildQuery(filters: QuestionFilters): string {
  const params = new URLSearchParams();
  if (filters.curriculum) params.set("curriculum", filters.curriculum);
  if (filters.subject) params.set("subject", filters.subject);
  if (filters.topic) params.set("topic", filters.topic);
  if (filters.type) params.set("type", filters.type);
  if (filters.difficulty !== undefined) params.set("difficulty", String(filters.difficulty));
  if (filters.q) params.set("q", filters.q);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  if (filters.sort) params.set("sort", filters.sort);
  return params.toString();
}

export async function listQuestions(filters: QuestionFilters = {}): Promise<QuestionListResponse> {
  const qs = buildQuery(filters);
  return apiFetch<QuestionListResponse>(`/api/v1/questions${qs ? `?${qs}` : ""}`);
}

export async function getQuestion(id: string | number): Promise<QuestionDetail> {
  return apiFetch<QuestionDetail>(`/api/v1/questions/${id}`);
}

export async function createQuestion(data: QuestionCreate): Promise<QuestionDetail> {
  return apiFetch<QuestionDetail>("/api/v1/questions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateQuestion(id: string | number, data: QuestionUpdate): Promise<QuestionDetail> {
  return apiFetch<QuestionDetail>(`/api/v1/questions/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteQuestion(id: string | number): Promise<void> {
  return apiFetch<void>(`/api/v1/questions/${id}`, { method: "DELETE" });
}

export async function getQuestionAnalysis(id: string | number): Promise<AnalysisResponse> {
  return apiFetch<AnalysisResponse>(`/api/v1/questions/${id}/analysis`);
}

export async function getSimilarQuestions(id: string | number, k = 10): Promise<SimilarQuestion[]> {
  return apiFetch<SimilarQuestion[]>(`/api/v1/questions/${id}/similar?k=${k}`);
}