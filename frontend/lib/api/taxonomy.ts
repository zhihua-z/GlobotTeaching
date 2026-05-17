import { apiFetch } from "./client";
import type { Curriculum, Subject, Topic, QuestionTypeMeta } from "@/types/question";

// Curricula
export async function listCurricula(): Promise<Curriculum[]> {
  return apiFetch<Curriculum[]>("/api/v1/curricula");
}

export async function createCurriculum(data: { code: string; name: string; description?: string }): Promise<Curriculum> {
  return apiFetch<Curriculum>("/api/v1/curricula", { method: "POST", body: JSON.stringify(data) });
}

export async function updateCurriculum(id: string, data: { name?: string; description?: string }): Promise<Curriculum> {
  return apiFetch<Curriculum>(`/api/v1/curricula/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function deleteCurriculum(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/curricula/${id}`, { method: "DELETE" });
}

// Subjects
export async function listSubjects(params?: { curriculum_id?: string }): Promise<Subject[]> {
  const qs = params?.curriculum_id ? `?curriculum_id=${params.curriculum_id}` : "";
  return apiFetch<Subject[]>(`/api/v1/subjects${qs}`);
}

export async function createSubject(data: { curriculum_id: string; code: string; name: string; description?: string }): Promise<Subject> {
  return apiFetch<Subject>("/api/v1/subjects", { method: "POST", body: JSON.stringify(data) });
}

export async function updateSubject(id: string, data: { name?: string; description?: string }): Promise<Subject> {
  return apiFetch<Subject>(`/api/v1/subjects/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function deleteSubject(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/subjects/${id}`, { method: "DELETE" });
}

// Topics
export async function listTopics(params?: { subject_id?: string; parent_id?: string }): Promise<Topic[]> {
  const searchParams = new URLSearchParams();
  if (params?.subject_id) searchParams.set("subject_id", params.subject_id);
  if (params?.parent_id) searchParams.set("parent_id", params.parent_id);
  const qs = searchParams.toString();
  return apiFetch<Topic[]>(`/api/v1/topics${qs ? `?${qs}` : ""}`);
}

export async function createTopic(data: { subject_id: string; parent_id?: string; name: string; slug: string; depth: number }): Promise<Topic> {
  return apiFetch<Topic>("/api/v1/topics", { method: "POST", body: JSON.stringify(data) });
}

export async function updateTopic(id: string, data: { name?: string; parent_id?: string }): Promise<Topic> {
  return apiFetch<Topic>(`/api/v1/topics/${id}`, { method: "PATCH", body: JSON.stringify(data) });
}

export async function deleteTopic(id: string, reassignTo?: string): Promise<void> {
  const qs = reassignTo ? `?reassign_to=${reassignTo}` : "";
  return apiFetch<void>(`/api/v1/topics/${id}${qs}`, { method: "DELETE" });
}

// Question Types
export async function listQuestionTypes(): Promise<QuestionTypeMeta[]> {
  return apiFetch<QuestionTypeMeta[]>("/api/v1/question-types");
}

export async function updateQuestionType(code: string, data: { label_zh?: string; description?: string }): Promise<QuestionTypeMeta> {
  return apiFetch<QuestionTypeMeta>(`/api/v1/question-types/${code}`, { method: "PATCH", body: JSON.stringify(data) });
}