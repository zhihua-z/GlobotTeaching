// Mock API service - all backend calls return mock data
// Used until the backend is fully implemented

import type {
  User,
  LoginResponse,
  ChatSession,
  ChatMessage,
  PracticeSession,
  SubmitAnswerResponse,
  ReviewCard,
  MistakeItem,
  SubjectProgress,
  TodayRecommendation,
  DashboardSummary,
  HeatmapCell,
  WeaknessItem,
  TrendDataPoint,
  LegalArticle,
  ProfileL1,
  ProfileL2,
  ProfileL3,
  ProfileEvent,
  PipelineRun,
  PipelineStage,
  QuestionDraft,
  PromptTemplate,
  EvalSet,
  EvalRun,
  EvalCase,
  UserSettings,
  AdminOverview,
} from "@/lib/types/api";
import type { QuestionListItem, QuestionListResponse, QuestionDetail, AnalysisResponse, SimilarQuestion } from "@/src/types/question";

const MOCK_DELAY = 300;

function delay(ms = MOCK_DELAY): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

// ============ Mock Data ============

const MOCK_SUBJECTS: Record<string, string> = {
  civil: "民法",
  criminal: "刑法",
  admin: "行政法",
  commercial: "商经法",
  intl: "三国法",
  theory: "理论法",
  crim_proc: "刑诉",
  civ_proc: "民诉",
};

const MOCK_USER: User = {
  id: 1,
  email: "zhihua@globot.com",
  name: "Zhihua",
  role: "admin",
};

const MOCK_CHAT_SESSIONS: ChatSession[] = [
  { id: "s1", subject: "civil", title: "民法侵权责任", created_at: "2026-05-16T10:00:00Z", updated_at: "2026-05-16T10:30:00Z", message_count: 8 },
  { id: "s2", subject: "criminal", title: "刑法故意与过失", created_at: "2026-05-15T14:00:00Z", updated_at: "2026-05-15T14:45:00Z", message_count: 12 },
  { id: "s3", subject: "admin", title: "行政许可程序", created_at: "2026-05-14T09:00:00Z", updated_at: "2026-05-14T09:20:00Z", message_count: 5 },
];

const MOCK_MESSAGES: Record<string, ChatMessage[]> = {
  s1: [
    { id: "m1", session_id: "s1", role: "user", content: "请解释民法中的侵权责任构成要件", created_at: "2026-05-16T10:00:00Z" },
    { id: "m2", session_id: "s1", role: "assistant", content: "侵权责任的构成要件包括以下四个方面：\n\n1. **违法行为**：行为人的行为违反了法律的规定\n2. **损害事实**：他人的财产或人身权益受到了实际损害\n3. **因果关系**：违法行为与损害事实之间存在因果关系\n4. **主观过错**：行为人主观上存在故意或过失\n\n> 《民法典》第1165条：行为人因过错侵害他人民事权益造成损害的，应当承担侵权责任。", created_at: "2026-05-16T10:00:05Z", citations: [{ type: "article", id: "1065", title: "民法典第1165条" }] },
    { id: "m3", session_id: "s1", role: "user", content: "能否举例说明？", created_at: "2026-05-16T10:05:00Z" },
    { id: "m4", session_id: "s1", role: "assistant", content: "例如：甲在开车时因看手机（过错）撞伤行人乙（损害），甲的行为违反了交通法规（违法），甲的看手机行为与乙受伤之间有直接因果关系。\n\n相关题目：[Q345](/questions/345) - 侵权责任案例分析", created_at: "2026-05-16T10:05:03Z", citations: [{ type: "question", id: "345", title: "Q345 侵权责任案例分析" }] },
  ],
  s2: [
    { id: "m5", session_id: "s2", role: "user", content: "刑法中故意和过失的区别是什么？", created_at: "2026-05-15T14:00:00Z" },
    { id: "m6", session_id: "s2", role: "assistant", content: "## 故意与过失的区别\n\n### 故意\n- **直接故意**：明知自己的行为会发生危害社会的结果，并且希望这种结果发生\n- **间接故意**：明知自己的行为可能发生危害结果，并且放任这种结果发生\n\n### 过失\n- **疏忽大意的过失**：应当预见自己的行为可能发生危害结果，因为疏忽大意而没有预见\n- **过于自信的过失**：已经预见而轻信能够避免\n\n关键区别在于**意志因素**：故意是'希望或放任'，过失是'疏忽或轻信'。", created_at: "2026-05-15T14:00:10Z" },
  ],
  s3: [
    { id: "m7", session_id: "s3", role: "user", content: "行政许可的设定权限是怎样的？", created_at: "2026-05-14T09:00:00Z" },
    { id: "m8", session_id: "s3", role: "assistant", content: "## 行政许可设定权限\n\n根据《行政许可法》，行政许可的设定权限如下：\n\n1. **法律**：可以设定行政许可\n2. **行政法规**：在尚未制定法律的情况下，可以设定行政许可\n3. **地方性法规**：在尚未制定法律、行政法规的情况下，可以设定行政许可\n4. **省、自治区、直辖市人民政府规章**：可以设定**临时性**行政许可\n\n> 部门规章**不得**设定行政许可。", created_at: "2026-05-14T09:00:08Z", citations: [{ type: "article", id: "2001", title: "行政许可法" }] },
  ],
};

const MOCK_PRACTICE_SESSIONS: PracticeSession[] = [
  { id: "ps1", subject: "civil", mode: "recommended", status: "in_progress", created_at: "2026-05-16T08:00:00Z", question_ids: [101, 102, 103, 104, 105], current_index: 2, answers: [] },
  { id: "ps2", subject: "criminal", mode: "weakness", status: "finished", created_at: "2026-05-15T10:00:00Z", question_ids: [201, 202, 203], current_index: 3, answers: [{ question_id: 201, answer: "A", time_spent_ms: 30000, correct: true, submitted_at: "2026-05-15T10:05:00Z" }, { question_id: 202, answer: "B", time_spent_ms: 45000, correct: false, submitted_at: "2026-05-15T10:06:00Z" }, { question_id: 203, answer: "C", time_spent_ms: 20000, correct: true, submitted_at: "2026-05-15T10:07:00Z" }] },
];

const MOCK_REVIEW_CARDS: ReviewCard[] = [
  { topic_path: "民法/物权编/善意取得", due_at: "2026-05-17T00:00:00Z", related_question_id: 345, stability: 0.8, difficulty: 0.3, subject: "civil", question_stem: "下列关于善意取得的说法，正确的是？", question_options: { A: "善意取得只能适用于动产", B: "善意取得中受让人须为善意", C: "善意取得无需支付合理价款", D: "善意取得不适用于不动产" }, question_answer: "B", question_type: "single_choice" },
  { topic_path: "民法/合同编/违约责任", due_at: "2026-05-17T00:00:00Z", related_question_id: 346, stability: 0.6, difficulty: 0.5, subject: "civil", question_stem: "违约责任的归责原则是？", question_options: { A: "过错责任原则", B: "无过错责任原则", C: "公平责任原则", D: "严格责任原则" }, question_answer: "D", question_type: "single_choice" },
  { topic_path: "刑法/总则/犯罪构成", due_at: "2026-05-17T00:00:00Z", related_question_id: 201, stability: 0.4, difficulty: 0.7, subject: "criminal", question_stem: "下列选项中，属于犯罪构成要件的是？", question_options: { A: "犯罪主体", B: "犯罪动机", C: "犯罪目的", D: "犯罪手段" }, question_answer: "A", question_type: "single_choice" },
];

const MOCK_MISTAKES: MistakeItem[] = [
  { question_id: 202, stem_preview: "下列关于犯罪未遂的说法正确的是...", subject: "criminal", error_count: 3, last_mistake_at: "2026-05-15T10:06:00Z", is_mastered: false },
  { question_id: 401, stem_preview: "根据《行政诉讼法》，下列哪些行为属于行政诉讼受案范围？", subject: "admin", error_count: 2, last_mistake_at: "2026-05-14T15:00:00Z", is_mastered: false },
  { question_id: 501, stem_preview: "关于公司董事义务的说法，错误的是？", subject: "commercial", error_count: 1, last_mistake_at: "2026-05-13T11:00:00Z", is_mastered: true },
];

const MOCK_PROGRESS: SubjectProgress[] = [
  { subject_code: "civil", subject_name: "民法", percentage: 60, current_chapter: "物权编/善意取得", estimated_completion: "2026-06-20" },
  { subject_code: "criminal", subject_name: "刑法", percentage: 30, current_chapter: "总则/犯罪构成", estimated_completion: "2026-07-10" },
  { subject_code: "admin", subject_name: "行政法", percentage: 20, current_chapter: "行政许可", estimated_completion: "2026-07-25" },
  { subject_code: "commercial", subject_name: "商经法", percentage: 15, current_chapter: "公司法", estimated_completion: "2026-08-01" },
  { subject_code: "intl", subject_name: "三国法", percentage: 10, current_chapter: "国际公法", estimated_completion: "2026-08-15" },
  { subject_code: "theory", subject_name: "理论法", percentage: 25, current_chapter: "法理学", estimated_completion: "2026-07-20" },
  { subject_code: "crim_proc", subject_name: "刑诉", percentage: 35, current_chapter: "侦查程序", estimated_completion: "2026-07-05" },
  { subject_code: "civ_proc", subject_name: "民诉", percentage: 40, current_chapter: "一审程序", estimated_completion: "2026-06-30" },
];

const MOCK_LEGAL_ARTICLES: LegalArticle[] = [
  { id: "1065", number: "第1165条", title: "过错责任原则", content: "行为人因过错侵害他人民事权益造成损害的，应当承担侵权责任。依照法律规定推定行为人有过错，其不能证明自己没有过错的，应当承担侵权责任。", interpretation: "本条确立了侵权责任的一般归责原则——过错责任原则。注意与无过错责任原则（第1166条）的区别。", subject: "civil", is_high_freq: true, effective_date: "2021-01-01", related_question_ids: [345, 346] },
  { id: "1066", number: "第1166条", title: "无过错责任原则", content: "行为人造成他人民事权益损害，不论行为人有无过错，法律规定应当承担侵权责任的，依照其规定。", interpretation: "无过错责任原则仅限于法律明确规定的情形，如高度危险作业、环境污染等。", subject: "civil", is_high_freq: true, effective_date: "2021-01-01", related_question_ids: [347] },
  { id: "2001", number: "《行政许可法》第14条", title: "行政许可设定权限", content: "本法第十二条所列事项，法律可以设定行政许可。尚未制定法律的，行政法规可以设定行政许可。", interpretation: "部门规章不得设定行政许可。", subject: "admin", is_high_freq: true, effective_date: "2019-04-23", related_question_ids: [401] },
];

const MOCK_PROFILE_L1: ProfileL1 = { summary: "民法物权偏弱，刑法稳定，建议加强物权编和合同编练习。" };
const MOCK_PROFILE_L2: ProfileL2 = { markdown: "## 当前知识状态\n\n### 民法 (60%)\n- 物权编：正确率 45%，需加强\n- 合同编：正确率 65%，中等\n- 侵权责任编：正确率 80%，较好\n\n### 刑法 (30%)\n- 总则/犯罪构成：正确率 72%，较好\n- 分则/侵犯财产罪：正确率 58%，一般" };
const MOCK_PROFILE_L3: ProfileL3 = {
  subject: "civil",
  topics: [
    { topic_path: "民法/物权编/善意取得", mastery: 0.35, typical_errors: ["混淆善意取得与无权处分", "误以为善意取得不适用于不动产"], recent_attempts: 5 },
    { topic_path: "民法/物权编/抵押权", mastery: 0.5, typical_errors: ["登记对抗与登记生效混淆"], recent_attempts: 3 },
    { topic_path: "民法/合同编/违约责任", mastery: 0.65, typical_errors: [], recent_attempts: 4 },
  ],
};
const MOCK_PROFILE_EVENTS: ProfileEvent[] = [
  { id: "e1", type: "answer", timestamp: "2026-05-16T10:00:00Z", description: "回答了Q345（民法/善意取得）- 错误" },
  { id: "e2", type: "review", timestamp: "2026-05-16T09:00:00Z", description: "FSRS复习：民法/物权编 - 评分 Good" },
  { id: "e3", type: "answer", timestamp: "2026-05-15T14:00:00Z", description: "回答了Q201（刑法/犯罪构成）- 正确" },
];

const MOCK_PIPELINE_RUNS: PipelineRun[] = [
  { id: "pr1", input_file: "2022年法考真题.md", current_stage: "classify", status: "running", duration_sec: 45, question_count: 50, created_at: "2026-05-16T12:00:00Z" },
  { id: "pr2", input_file: "2021年法考真题.md", current_stage: "review_enqueue", status: "completed", duration_sec: 120, question_count: 45, created_at: "2026-05-15T10:00:00Z" },
  { id: "pr3", input_file: "2020年法考真题.md", current_stage: "parse", status: "failed", duration_sec: 30, question_count: 0, created_at: "2026-05-14T08:00:00Z" },
];
const MOCK_PIPELINE_STAGES: Record<string, PipelineStage[]> = {
  pr1: [
    { name: "parse", status: "completed", input: "2022年法考真题.md (50题)", output: "50 raw questions", logs: ["[OK] 解析完成"] },
    { name: "classify", status: "running", input: "50 raw questions", output: "processing...", logs: ["[INFO] 分类中..."] },
    { name: "rubric", status: "pending", input: "", output: "", logs: [] },
    { name: "variant", status: "pending", input: "", output: "", logs: [] },
    { name: "review_enqueue", status: "pending", input: "", output: "", logs: [] },
  ],
  pr2: [
    { name: "parse", status: "completed", input: "2021年法考真题.md (45题)", output: "45 raw questions", logs: ["[OK] 解析完成"] },
    { name: "classify", status: "completed", input: "45 raw questions", output: "45 classified", logs: ["[OK] 分类完成"] },
    { name: "rubric", status: "completed", input: "45 classified", output: "45 with rubric", logs: ["[OK] 评分标准生成完成"] },
    { name: "variant", status: "completed", input: "45 with rubric", output: "135 variants", logs: ["[OK] 变体生成完成"] },
    { name: "review_enqueue", status: "completed", input: "135 variants", output: "135 enqueued", logs: ["[OK] 已加入审核队列"] },
  ],
  pr3: [
    { name: "parse", status: "failed", input: "2020年法考真题.md", output: "0 questions", logs: ["[ERR] 文件格式不支持", "[ERR] 解析异常: Expected markdown table"] },
  ],
};

const MOCK_DRAFTS: QuestionDraft[] = [
  { id: "d1", stem_preview: "下列关于物权变动的说法，正确的是？", proposed_subject: "civil", proposed_topic: "物权编", ai_confidence: 0.95, status: "pending", created_at: "2026-05-16T12:00:00Z", source_file: "2022年法考真题.md", proposed_data: {} },
  { id: "d2", stem_preview: "关于正当防卫的认定，下列选项错误的是？", proposed_subject: "criminal", proposed_topic: "总则/正当防卫", ai_confidence: 0.88, status: "pending", created_at: "2026-05-16T12:01:00Z", source_file: "2022年法考真题.md", proposed_data: {} },
  { id: "d3", stem_preview: "根据《行政强制法》，行政强制的种类包括？", proposed_subject: "admin", proposed_topic: "行政强制", ai_confidence: 0.92, status: "approved", created_at: "2026-05-15T10:00:00Z", source_file: "2021年法考真题.md", proposed_data: {} },
  { id: "d4", stem_preview: "公司股东会决议无效的情形有？", proposed_subject: "commercial", proposed_topic: "公司法", ai_confidence: 0.76, status: "rejected", created_at: "2026-05-15T10:05:00Z", source_file: "2021年法考真题.md", proposed_data: {} },
];

const MOCK_PROMPTS: PromptTemplate[] = [
  { name: "chat_law_socratic", group: "chat", yaml: "system: \"你是一个法考辅导老师。采用苏格拉底式提问引导学生思考。\"\ntemperature: 0.7\nmax_tokens: 2048\n", version: 3, updated_at: "2026-05-10T00:00:00Z", change_note: "优化了法条引用格式" },
  { name: "classify", group: "pipeline", yaml: "system: \"将题目分类到正确的科目和知识点。\"\ntemperature: 0.3\nmax_tokens: 512\n", version: 2, updated_at: "2026-05-08T00:00:00Z", change_note: "增加分类规则" },
  { name: "rubric", group: "pipeline", yaml: "system: \"为题目生成评分标准。\"\ntemperature: 0.3\nmax_tokens: 1024\n", version: 1, updated_at: "2026-05-05T00:00:00Z", change_note: "初始版本" },
];

const MOCK_EVAL_SETS: EvalSet[] = [
  { id: "es1", name: "分类准确率测试集", target: "classify", created_at: "2026-05-01T00:00:00Z", run_count: 5 },
  { id: "es2", name: "评分标准生成测试集", target: "rubric", created_at: "2026-05-02T00:00:00Z", run_count: 3 },
];
const MOCK_EVAL_RUNS: EvalRun[] = [
  { id: "er1", set_id: "es1", status: "completed", accuracy: 0.92, recall: 0.88, created_at: "2026-05-15T00:00:00Z" },
  { id: "er2", set_id: "es1", status: "completed", accuracy: 0.85, recall: 0.82, created_at: "2026-05-10T00:00:00Z" },
  { id: "er3", set_id: "es2", status: "running", accuracy: 0, recall: 0, created_at: "2026-05-16T00:00:00Z" },
];
const MOCK_EVAL_CASES: EvalCase[] = [
  { id: "ec1", input: "下列关于物权变动的说法...", expected: "civil/物权编", actual: "civil/物权编", status: "passed" },
  { id: "ec2", input: "关于正当防卫的认定...", expected: "criminal/正当防卫", actual: "civil/侵权责任", status: "failed" },
  { id: "ec3", input: "根据《行政强制法》...", expected: "admin/行政强制", actual: "admin/行政强制", status: "passed" },
];

const MOCK_SETTINGS: UserSettings = {
  daily_hours: 3,
  target_exam_date: "2026-09-15",
  reminder_times: ["09:00", "14:00", "20:00"],
  email_enabled: true,
};

const MOCK_QUESTIONS: QuestionListItem[] = [
  { id: 101, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "civil", topic_path: ["民法", "物权编", "善意取得"], difficulty: 3, type: "single_choice", stem: "下列关于善意取得的说法，正确的是？", options: { A: "善意取得只能适用于动产", B: "善意取得中受让人须为善意", C: "善意取得无需支付合理价款", D: "善意取得不适用于不动产" }, answer: "B", rubric: null, solution: "根据《民法典》第311条，善意取得要求受让人受让时是善意的。", variants: [], source_origin: null, source_year: 2022, is_indeterminate: false, cited_articles: ["1065"], has_embedding: true },
  { id: 102, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "civil", topic_path: ["民法", "合同编", "违约责任"], difficulty: 4, type: "single_choice", stem: "违约责任的归责原则是？", options: { A: "过错责任原则", B: "无过错责任原则", C: "公平责任原则", D: "严格责任原则" }, answer: "D", rubric: null, solution: "违约责任适用严格责任原则，不以过错为要件。", variants: [], source_origin: null, source_year: 2022, is_indeterminate: false, cited_articles: [], has_embedding: true },
  { id: 201, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "criminal", topic_path: ["刑法", "总则", "犯罪构成"], difficulty: 3, type: "single_choice", stem: "下列选项中，属于犯罪构成要件的是？", options: { A: "犯罪主体", B: "犯罪动机", C: "犯罪目的", D: "犯罪手段" }, answer: "A", rubric: null, solution: "犯罪构成要件包括犯罪主体、主观方面、客体、客观方面。", variants: [], source_origin: null, source_year: 2021, is_indeterminate: false, cited_articles: [], has_embedding: true },
  { id: 202, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "criminal", topic_path: ["刑法", "总则", "未遂"], difficulty: 4, type: "single_choice", stem: "下列关于犯罪未遂的说法正确的是？", options: { A: "犯罪未遂不构成犯罪", B: "犯罪未遂可以比照既遂从轻处罚", C: "犯罪未遂等同于犯罪中止", D: "犯罪未遂必然免除处罚" }, answer: "B", rubric: null, solution: "根据《刑法》第23条，对于未遂犯，可以比照既遂犯从轻或者减轻处罚。", variants: [], source_origin: null, source_year: 2021, is_indeterminate: false, cited_articles: [], has_embedding: true },
  { id: 345, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "civil", topic_path: ["民法", "物权编", "善意取得"], difficulty: 4, type: "single_choice", stem: "甲将手机借给乙使用，乙擅自将手机卖给不知情的丙。丙是否取得所有权？", options: { A: "丙不能取得所有权", B: "丙可以善意取得所有权", C: "需要看丙是否支付了合理价格", D: "仅当甲追认时丙才能取得" }, answer: "B", rubric: null, solution: "丙构成善意取得。乙无权处分，但丙不知情且支付合理价格。", variants: [], source_origin: null, source_year: 2022, is_indeterminate: false, cited_articles: ["1065"], has_embedding: true },
  { id: 346, created_at: "2026-05-01T00:00:00Z", updated_at: "2026-05-01T00:00:00Z", curriculum: "FAKAO", subject: "civil", topic_path: ["民法", "合同编", "违约责任"], difficulty: 2, type: "multiple_choice", stem: "下列哪些属于违约责任的承担方式？", options: { A: "继续履行", B: "赔偿损失", C: "支付违约金", D: "消除危险" }, answer: "A,B,C", rubric: null, solution: "违约责任的承担方式包括继续履行、赔偿损失、支付违约金等。", variants: [], source_origin: null, source_year: 2021, is_indeterminate: false, cited_articles: [], has_embedding: true },
];

// ============ Mock API Functions ============

// --- Auth ---
export async function mockLogin(): Promise<LoginResponse> {
  await delay();
  return { user: MOCK_USER, token: "mock-token-xxx" };
}

export async function mockLogout(): Promise<void> {
  await delay();
}

export async function mockGetMe(): Promise<User> {
  await delay();
  return MOCK_USER;
}

// --- Chat ---
export async function mockGetChatSessions(): Promise<ChatSession[]> {
  await delay();
  return MOCK_CHAT_SESSIONS;
}

export async function mockCreateChatSession(subject: string, title?: string): Promise<ChatSession> {
  await delay();
  const session: ChatSession = {
    id: `s${Date.now()}`,
    subject,
    title: title || subject,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    message_count: 0,
  };
  MOCK_CHAT_SESSIONS.unshift(session);
  MOCK_MESSAGES[session.id] = [];
  return session;
}

export async function mockGetChatMessages(sessionId: string): Promise<ChatMessage[]> {
  await delay();
  return MOCK_MESSAGES[sessionId] || [];
}

export async function mockSendMessage(sessionId: string, content: string): Promise<ChatMessage> {
  await delay(1000);
  const userMsg: ChatMessage = {
    id: `m${Date.now()}`,
    session_id: sessionId,
    role: "user",
    content,
    created_at: new Date().toISOString(),
  };
  if (!MOCK_MESSAGES[sessionId]) MOCK_MESSAGES[sessionId] = [];
  MOCK_MESSAGES[sessionId].push(userMsg);

  const assistantMsg: ChatMessage = {
    id: `m${Date.now() + 1}`,
    session_id: sessionId,
    role: "assistant",
    content: "这是一个模拟回复。您提到了\"" + content.slice(0, 30) + "...\"相关问题。\n\n在法考中，这个知识点属于重要考点。建议您结合相关法条和典型案例来理解。\n\n> 提示：可以尝试在 `/practice` 中练习相关题目。",
    created_at: new Date().toISOString(),
  };
  MOCK_MESSAGES[sessionId].push(assistantMsg);
  return assistantMsg;
}

export async function mockDeleteChatSession(sessionId: string): Promise<void> {
  await delay();
  const idx = MOCK_CHAT_SESSIONS.findIndex((s) => s.id === sessionId);
  if (idx >= 0) MOCK_CHAT_SESSIONS.splice(idx, 1);
  delete MOCK_MESSAGES[sessionId];
}

// --- Practice ---
export async function mockGetPracticeSessions(): Promise<PracticeSession[]> {
  await delay();
  return MOCK_PRACTICE_SESSIONS;
}

export async function mockCreatePracticeSession(data: {
  subject: string;
  mode: string;
  type: string[];
  count: number;
}): Promise<PracticeSession> {
  await delay();
  const session: PracticeSession = {
    id: `ps${Date.now()}`,
    subject: data.subject,
    mode: data.mode,
    status: "in_progress",
    created_at: new Date().toISOString(),
    question_ids: [101, 102, 103].slice(0, data.count),
    current_index: 0,
    answers: [],
  };
  MOCK_PRACTICE_SESSIONS.unshift(session);
  return session;
}

export async function mockGetPracticeSession(id: string): Promise<PracticeSession> {
  await delay();
  return MOCK_PRACTICE_SESSIONS.find((s) => s.id === id) || MOCK_PRACTICE_SESSIONS[0];
}

export async function mockSubmitAnswer(
  sessionId: string,
  questionId: number,
  answer: string
): Promise<SubmitAnswerResponse> {
  await delay();
  const correct = answer === (MOCK_QUESTIONS.find((q) => q.id === questionId)?.answer || "A");
  return {
    correct,
    rubric_breakdown: {},
    profile_event_id: `pe${Date.now()}`,
  };
}

export async function mockFinishPracticeSession(sessionId: string): Promise<void> {
  await delay();
  const session = MOCK_PRACTICE_SESSIONS.find((s) => s.id === sessionId);
  if (session) session.status = "finished";
}

// --- Review ---
export async function mockGetReviewDue(subject?: string): Promise<ReviewCard[]> {
  await delay();
  if (subject) return MOCK_REVIEW_CARDS.filter((c) => c.subject === subject);
  return MOCK_REVIEW_CARDS;
}

export async function mockRateReview(_topicPath: string, _rating: string): Promise<void> {
  await delay();
}

// --- Mistakes ---
export async function mockGetMistakes(): Promise<MistakeItem[]> {
  await delay();
  return MOCK_MISTAKES;
}

export async function mockMarkMastered(questionId: number): Promise<void> {
  await delay();
  const m = MOCK_MISTAKES.find((m) => m.question_id === questionId);
  if (m) m.is_mastered = true;
}

// --- Progress ---
export async function mockGetProgress(): Promise<SubjectProgress[]> {
  await delay();
  return MOCK_PROGRESS;
}

// --- Dashboard ---
export async function mockGetTodayRecommendation(): Promise<TodayRecommendation> {
  await delay();
  return {
    review_due: MOCK_REVIEW_CARDS,
    suggested_practice: MOCK_PRACTICE_SESSIONS.filter((s) => s.status === "in_progress"),
    gaps: ["民法/物权编/善意取得 - 正确率偏低", "刑法/总则/未遂 - 需加强", "行政法/行政许可 - 新知识点"],
  };
}

export async function mockGetDashboardSummary(): Promise<DashboardSummary> {
  await delay();
  return {
    days_to_exam: 121,
    streak: 7,
    weekly_stats: { question_count: 45, correct_rate: 0.72, review_completion_rate: 0.85 },
  };
}

export async function mockGetHeatmap(): Promise<HeatmapCell[]> {
  await delay();
  return [
    { subject: "civil", topic_path: "民法/物权编", stability: 0.6, mastery: 0.45 },
    { subject: "civil", topic_path: "民法/合同编", stability: 0.7, mastery: 0.65 },
    { subject: "criminal", topic_path: "刑法/总则", stability: 0.8, mastery: 0.72 },
    { subject: "admin", topic_path: "行政法/行政许可", stability: 0.5, mastery: 0.4 },
  ];
}

export async function mockGetWeaknesses(): Promise<WeaknessItem[]> {
  await delay();
  return [
    { topic: "物权编/善意取得", subject: "civil", score: 0.35, suggestion: "建议复习民法典第311条" },
    { topic: "总则/未遂", subject: "criminal", score: 0.45, suggestion: "建议练习相关真题" },
    { topic: "行政许可", subject: "admin", score: 0.5, suggestion: "建议系统学习行政许可法" },
  ];
}

export async function mockGetTrends(): Promise<TrendDataPoint[]> {
  await delay();
  return [
    { week: "W18", value: 30 }, { week: "W19", value: 45 }, { week: "W20", value: 38 }, { week: "W21", value: 52 },
  ];
}

// --- Legal Articles ---
export async function mockGetLegalArticles(q?: string, subject?: string): Promise<LegalArticle[]> {
  await delay();
  let result = [...MOCK_LEGAL_ARTICLES];
  if (q) result = result.filter((a) => a.number.includes(q) || a.title.includes(q) || a.content.includes(q));
  if (subject) result = result.filter((a) => a.subject === subject);
  return result;
}

export async function mockGetLegalArticle(id: string): Promise<LegalArticle> {
  await delay();
  return MOCK_LEGAL_ARTICLES.find((a) => a.id === id) || MOCK_LEGAL_ARTICLES[0];
}

// --- Profile ---
export async function mockGetProfileL1(): Promise<ProfileL1> {
  await delay();
  return MOCK_PROFILE_L1;
}

export async function mockGetProfileL2(): Promise<ProfileL2> {
  await delay();
  return MOCK_PROFILE_L2;
}

export async function mockGetProfileL3(subject?: string): Promise<ProfileL3> {
  await delay();
  return subject ? { ...MOCK_PROFILE_L3, subject } : MOCK_PROFILE_L3;
}

export async function mockGetProfileEvents(): Promise<ProfileEvent[]> {
  await delay();
  return MOCK_PROFILE_EVENTS;
}

// --- Pipeline ---
export async function mockGetPipelineRuns(): Promise<PipelineRun[]> {
  await delay();
  return MOCK_PIPELINE_RUNS;
}

export async function mockGetPipelineRun(id: string): Promise<{ run: PipelineRun; stages: PipelineStage[] }> {
  await delay();
  const run = MOCK_PIPELINE_RUNS.find((r) => r.id === id) || MOCK_PIPELINE_RUNS[0];
  const stages = MOCK_PIPELINE_STAGES[id] || [];
  return { run, stages };
}

// --- Review Queue ---
export async function mockGetReviewQueue(status?: string): Promise<QuestionDraft[]> {
  await delay();
  if (status) return MOCK_DRAFTS.filter((d) => d.status === status);
  return MOCK_DRAFTS;
}

export async function mockGetDraft(id: string): Promise<QuestionDraft> {
  await delay();
  return MOCK_DRAFTS.find((d) => d.id === id) || MOCK_DRAFTS[0];
}

export async function mockApproveDraft(id: string): Promise<void> {
  await delay();
  const d = MOCK_DRAFTS.find((d) => d.id === id);
  if (d) d.status = "approved";
}

export async function mockRejectDraft(id: string): Promise<void> {
  await delay();
  const d = MOCK_DRAFTS.find((d) => d.id === id);
  if (d) d.status = "rejected";
}

// --- Prompts ---
export async function mockGetPrompts(): Promise<PromptTemplate[]> {
  await delay();
  return MOCK_PROMPTS;
}

// --- Evals ---
export async function mockGetEvalSets(): Promise<EvalSet[]> {
  await delay();
  return MOCK_EVAL_SETS;
}

export async function mockGetEvalRuns(setId?: string): Promise<EvalRun[]> {
  await delay();
  if (setId) return MOCK_EVAL_RUNS.filter((r) => r.set_id === setId);
  return MOCK_EVAL_RUNS;
}

export async function mockGetFailedCases(runId?: string): Promise<EvalCase[]> {
  await delay();
  return MOCK_EVAL_CASES.filter((c) => c.status === "failed");
}

export async function mockRunEval(data: { set_id: string; target: string }): Promise<EvalRun> {
  await delay(500);
  const newRun: EvalRun = {
    id: `er${Date.now()}`,
    set_id: data.set_id,
    status: "running",
    accuracy: 0,
    recall: 0,
    created_at: new Date().toISOString(),
  };
  MOCK_EVAL_RUNS.unshift(newRun);
  return newRun;
}

// --- Settings ---
export async function mockGetSettings(): Promise<UserSettings> {
  await delay();
  return MOCK_SETTINGS;
}

export async function mockUpdateSettings(data: Partial<UserSettings>): Promise<UserSettings> {
  await delay();
  Object.assign(MOCK_SETTINGS, data);
  return MOCK_SETTINGS;
}

// --- Admin Overview ---
export async function mockGetAdminOverview(): Promise<AdminOverview> {
  await delay();
  return {
    total_questions: 1450,
    subject_distribution: { civil: 320, criminal: 280, admin: 180, commercial: 200, intl: 120, theory: 150, crim_proc: 100, civ_proc: 100 },
    review_queue_pending: 124,
    pipeline_last_24h: 3,
    latest_eval_score: 0.92,
  };
}

// --- Questions (override from existing) ---
export async function mockListQuestions(): Promise<QuestionListResponse> {
  await delay();
  return {
    items: MOCK_QUESTIONS,
    total: MOCK_QUESTIONS.length,
    page: 1,
    page_size: 20,
  };
}

export async function mockGetQuestionById(id: number): Promise<QuestionDetail> {
  await delay();
  return MOCK_QUESTIONS.find((q) => q.id === id) || MOCK_QUESTIONS[0];
}

// ============ Aggregated API object for easy access ============
export const mockApi = {
  // Auth
  login: mockLogin,
  logout: mockLogout,
  getMe: mockGetMe,
  // Chat
  getChatSessions: mockGetChatSessions,
  createChatSession: mockCreateChatSession,
  getChatMessages: mockGetChatMessages,
  sendMessage: mockSendMessage,
  deleteChatSession: mockDeleteChatSession,
  // Practice
  getPracticeSessions: mockGetPracticeSessions,
  createPracticeSession: mockCreatePracticeSession,
  getPracticeSession: mockGetPracticeSession,
  submitAnswer: mockSubmitAnswer,
  finishPracticeSession: mockFinishPracticeSession,
  // Review
  getReviewDue: mockGetReviewDue,
  rateReview: mockRateReview,
  // Mistakes
  getMistakes: mockGetMistakes,
  markMastered: mockMarkMastered,
  // Progress
  getProgress: mockGetProgress,
  // Dashboard
  getTodayRecommendation: mockGetTodayRecommendation,
  getDashboardSummary: mockGetDashboardSummary,
  getHeatmap: mockGetHeatmap,
  getWeaknesses: mockGetWeaknesses,
  getTrends: mockGetTrends,
  // Legal Articles
  getLegalArticles: mockGetLegalArticles,
  getLegalArticle: mockGetLegalArticle,
  // Profile
  getProfileL1: mockGetProfileL1,
  getProfileL2: mockGetProfileL2,
  getProfileL3: mockGetProfileL3,
  getProfileEvents: mockGetProfileEvents,
  // Pipeline
  getPipelineRuns: mockGetPipelineRuns,
  getPipelineRun: mockGetPipelineRun,
  // Review Queue
  getReviewQueue: mockGetReviewQueue,
  getDraft: mockGetDraft,
  approveDraft: mockApproveDraft,
  rejectDraft: mockRejectDraft,
  // Prompts
  getPrompts: mockGetPrompts,
  // Evals
  getEvalSets: mockGetEvalSets,
  getEvalRuns: mockGetEvalRuns,
  getFailedCases: mockGetFailedCases,
  runEval: mockRunEval,
  // Settings
  getSettings: mockGetSettings,
  updateSettings: mockUpdateSettings,
  // Admin Overview
  getAdminOverview: mockGetAdminOverview,
  // Questions
  listQuestions: mockListQuestions,
  getQuestionById: mockGetQuestionById,
};
