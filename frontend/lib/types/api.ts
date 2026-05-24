// Shared API types for the entire frontend (mocked)

// ============ Auth ============
export interface User {
  id: number;
  email: string;
  name: string;
  role: "student" | "admin";
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
}

// ============ Chat ============
export interface ChatSession {
  id: string;
  subject: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  quoted_question_ids?: number[];
  quoted_article_ids?: string[];
  citations?: Citation[];
}

export interface Citation {
  type: "question" | "article";
  id: string;
  title: string;
}

export interface CreateSessionRequest {
  subject: string;
  title?: string;
}

export interface SendMessageRequest {
  content: string;
  quoted_question_ids?: number[];
  quoted_article_ids?: string[];
}

// ============ Practice ============
export interface CreatePracticeSessionRequest {
  subject: string;
  mode: "recommended" | "weakness" | "custom";
  topic_path?: string[];
  type: string[];
  count: number;
}

export interface PracticeSession {
  id: string;
  subject: string;
  mode: string;
  status: "in_progress" | "finished";
  created_at: string;
  question_ids: number[];
  current_index: number;
  answers: PracticeAnswer[];
}

export interface PracticeAnswer {
  question_id: number;
  answer: string;
  time_spent_ms: number;
  flagged?: boolean;
  correct: boolean;
  submitted_at?: string;
}

export interface SubmitAnswerRequest {
  question_id: number;
  answer: string;
  time_spent_ms: number;
  flagged?: boolean;
}

export interface SubmitAnswerResponse {
  correct: boolean;
  rubric_breakdown: Record<string, unknown>;
  profile_event_id: string;
}

// ============ Review (FSRS) ============
export interface ReviewCard {
  topic_path: string;
  due_at: string;
  related_question_id: number;
  stability: number;
  difficulty: number;
  subject: string;
  question_stem: string;
  question_options: Record<string, string>;
  question_answer: string;
  question_type: string;
}

export type FsrsRating = "again" | "hard" | "good" | "easy";

export interface RateReviewRequest {
  topic_path: string;
  rating: FsrsRating;
  related_question_id?: number;
}

// ============ Mistakes ============
export interface MistakeItem {
  question_id: number;
  stem_preview: string;
  subject: string;
  error_count: number;
  last_mistake_at: string;
  is_mastered: boolean;
}

// ============ Progress ============
export interface SubjectProgress {
  subject_code: string;
  subject_name: string;
  percentage: number;
  current_chapter: string;
  estimated_completion: string;
}

export interface UpdateProgressRequest {
  current_chapter_path?: string;
  daily_hours?: number;
  target_exam_date?: string;
}

// ============ Dashboard ============
export interface TodayRecommendation {
  review_due: ReviewCard[];
  suggested_practice: PracticeSession[];
  gaps: string[];
}

export interface DashboardSummary {
  days_to_exam: number;
  streak: number;
  weekly_stats: {
    question_count: number;
    correct_rate: number;
    review_completion_rate: number;
  };
}

export interface HeatmapCell {
  subject: string;
  topic_path: string;
  stability: number;
  mastery: number;
}

export interface WeaknessItem {
  topic: string;
  subject: string;
  score: number;
  suggestion: string;
}

export interface TrendDataPoint {
  week: string;
  value: number;
}

// ============ Legal Articles ============
export interface LegalArticle {
  id: string;
  number: string;
  title: string;
  content: string;
  interpretation: string;
  subject: string;
  is_high_freq: boolean;
  effective_date: string;
  related_question_ids: number[];
}

// ============ Profile ============
export interface ProfileL1 {
  summary: string;
}

export interface ProfileL2 {
  markdown: string;
}

export interface ProfileL3Topic {
  topic_path: string;
  mastery: number;
  typical_errors: string[];
  recent_attempts: number;
}

export interface ProfileL3 {
  subject: string;
  topics: ProfileL3Topic[];
}

export interface ProfileEvent {
  id: string;
  type: string;
  timestamp: string;
  description: string;
}

// ============ Pipeline ============
export interface PipelineRun {
  id: string;
  input_file: string;
  current_stage: string;
  status: "running" | "completed" | "failed";
  duration_sec: number;
  question_count: number;
  created_at: string;
}

export interface PipelineStage {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  input: string;
  output: string;
  logs: string[];
}

// ============ Review Queue ============
export interface QuestionDraft {
  id: string;
  stem_preview: string;
  proposed_subject: string;
  proposed_topic: string;
  ai_confidence: number;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  source_file: string;
  proposed_data: Record<string, unknown>;
}

export interface ApproveDraftResponse {
  question_id: number;
}

// ============ Prompts ============
export interface PromptTemplate {
  name: string;
  group: string;
  yaml: string;
  version: number;
  updated_at: string;
  change_note: string;
}

// ============ Evals ============
export interface EvalSet {
  id: string;
  name: string;
  target: string;
  created_at: string;
  run_count: number;
}

export interface EvalRun {
  id: string;
  set_id: string;
  status: "running" | "completed" | "failed";
  accuracy: number;
  recall: number;
  created_at: string;
}

export interface EvalCase {
  id: string;
  input: string;
  expected: string;
  actual: string;
  status: "passed" | "failed";
}

// ============ Settings ============
export interface UserSettings {
  daily_hours: number;
  target_exam_date: string;
  reminder_times: string[];
  email_enabled: boolean;
}

// ============ Admin Overview ============
export interface AdminOverview {
  total_questions: number;
  subject_distribution: Record<string, number>;
  review_queue_pending: number;
  pipeline_last_24h: number;
  latest_eval_score: number | null;
}