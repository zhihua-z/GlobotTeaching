/** Mirrors the backend QuestionType enum */
export type QuestionType =
  | "multiple_choice"
  | "single_choice"
  | "true_false"
  | "fill_blank"
  | "short_answer"
  | "essay"
  | "code"
  | "matching"
  | "ordering";

export interface QuestionListItem {
  id: number;
  created_at: string;
  updated_at: string;
  curriculum: string;
  subject: string;
  topic_path: string[];
  difficulty: number;
  type: QuestionType;
  stem: string;
  options: Record<string, unknown> | null;
  answer: string;
  rubric: Record<string, unknown> | null;
  solution: string | null;
  variants: string[];
  source_origin: string | null;
  source_year: number | null;
  is_indeterminate: boolean;
  cited_articles: string[];
  has_embedding: boolean;
}

export interface QuestionListResponse {
  items: QuestionListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface QuestionDetail extends QuestionListItem {
  // Same as list item, kept for clarity
}

/** Alias for consistency with backend schema naming */
export type QuestionResponse = QuestionDetail;

export interface SimilarQuestion {
  id: number;
  stem: string;
  similarity: number;
}

export interface AnalysisResponse {
  question: QuestionDetail;
  stats: {
    length_chars: number;
    option_count: number;
    estimated_read_time_sec: number;
  };
  similar: SimilarQuestion[];
  siblings_in_topic: number;
  difficulty_distribution_in_topic: Record<string, number>;
  ai_breakdown: null | {
    summary: string;
    key_concepts: string[];
    common_mistakes: string[];
  };
}

export interface QuestionCreate {
  curriculum: string;
  subject: string;
  topic_path?: string[];
  difficulty?: number;
  type: QuestionType;
  stem: string;
  options?: Record<string, unknown> | null;
  answer: string;
  rubric?: Record<string, unknown> | null;
  solution?: string | null;
  variants?: string[];
  source_origin?: string | null;
  source_year?: number | null;
  is_indeterminate?: boolean;
  cited_articles?: string[];
}

export interface QuestionUpdate {
  curriculum?: string;
  subject?: string;
  topic_path?: string[];
  difficulty?: number;
  type?: QuestionType;
  stem?: string;
  options?: Record<string, unknown> | null;
  answer?: string;
  rubric?: Record<string, unknown> | null;
  solution?: string | null;
  variants?: string[];
  source_origin?: string | null;
  source_year?: number | null;
  is_indeterminate?: boolean;
  cited_articles?: string[];
}

export interface QuestionFilters {
  curriculum?: string;
  subject?: string;
  topic?: string;
  type?: string;
  difficulty?: number;
  q?: string;
  page?: number;
  page_size?: number;
  sort?: string;
}

/** Taxonomy types */
export interface Curriculum {
  id: string;
  code: string;
  name: string;
  description: string | null;
}

export interface Subject {
  id: string;
  curriculum_id: string;
  code: string;
  name: string;
  description: string | null;
}

export interface Topic {
  id: string;
  subject_id: string;
  parent_id: string | null;
  name: string;
  slug: string;
  depth: number;
}

export interface QuestionTypeMeta {
  code: string;
  label_en: string;
  label_zh: string;
  requires_options: boolean;
  requires_rubric: boolean;
  description: string | null;
}