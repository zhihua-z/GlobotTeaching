# GlobotTeaching 法考题库实施计划

## 1. 背景与目标

当前项目有一个 PostgreSQL 数据库（`questions` 表）和基础的 FastAPI + Next.js 前后端框架。docs 目录下已有从 2014、2020、2021、2022 年的法考客观题真题 Markdown 文件。

**目标：**
1. 设计一套分类方案，将 Markdown 中的试题解析后入库
2. 编写解析脚本，批量将 Markdown → 结构化 JSON → 数据库
3. 提供一个**题目分析页面**（查看单题详情）
4. 提供一个**后台管理页面**（CRUD 管理所有题目、科目、题目类型）

---

## 2. 题目分类方案

基于现有的 `questions` 表结构和法考真题格式，分类层次如下：

| 层级 | 数据库字段 | 说明 | 示例值 |
|------|-----------|------|--------|
| 大纲/考纲 | `curriculum` | 整份试卷所属的考试 | `"2022年国家统一法律职业资格考试"` |
| 卷别 | `subject` | 试卷一/试卷二 | `"试卷一"` |
| 题型分类 | `topic_path[0]` | 题型大类 | `"单项选择题"`, `"多项选择题"`, `"不定项选择题"` |
| 难度 | `difficulty` | 静默导入后可手动调整 | `1-5` |
| 题目类型 | `type` | 系统题型枚举 | `"single_choice"` |
| 题目内容 | `stem` | 题面 | 第1题正文 |
| 选项 | `options` | JSON: `{"A":"...","B":"...","C":"...","D":"..."}` | |
| 答案 | `answer` | 正确答案 | `"B"` |
| 来源 | `source_origin` | 回忆版/官方版 | `"2022年法考客观题真题（回忆版）"` |

### 分类树状图

```
curriculum: "2022年国家统一法律职业资格考试"
├── subject: "试卷一"
│   ├── topic_path: ["单项选择题"]  →  type: single_choice
│   ├── topic_path: ["多项选择题"]  →  type: multiple_choice
│   └── topic_path: ["不定项选择题"] → type: multiple_choice
└── subject: "试卷二"
    ├── topic_path: ["单项选择题"]  →  type: single_choice
    ├── topic_path: ["多项选择题"]  →  type: multiple_choice
    └── topic_path: ["不定项选择题"] → type: multiple_choice
```

**注意**：多项选择题和不定项选择题虽然在数据库中都使用 `multiple_choice` 类型，但它们的评分规则不同。可以在 `rubric` 字段中标注 `{"correct_count": 2}` 或 `{"is_indefinite": true}` 来区分。

---

## 3. 实施步骤

### Phase 1: 后端 API 完善

#### Step 1.1 — 创建 Question CRUD Router

在 `backend/app/routers/` 下创建 `questions.py`，提供以下端点：

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/questions` | 分页查询（支持 curriculum / subject / type 过滤） |
| GET | `/api/questions/{id}` | 单题详情 |
| POST | `/api/questions` | 创建题目 |
| PUT | `/api/questions/{id}` | 更新题目 |
| DELETE | `/api/questions/{id}` | 删除题目 |
| GET | `/api/curriculums` | 列出所有 curriculum（去重） |
| GET | `/api/subjects?curriculum=xxx` | 列出某大纲下的所有 subject |
| GET | `/api/question-types` | 列出所有题型枚举值 |

#### Step 1.2 — 注册 Router

在 `backend/app/main.py` 中引入 `questions.py` 的 router。

### Phase 2: Markdown → JSON 解析脚本

#### Step 2.1 — 设计数据流

```
Markdown 文件  →  Python 解析脚本  →  JSON Lines 文件  →  API 批量导入 / 直接 SQL
```

#### Step 2.2 — 解析脚本结构

在 `backend/scripts/` 下创建 `parse_fakao.py`：

```python
# 核心逻辑：
# 1. 读取 .md 文件，按标题层级识别：
#    - `##` → curriculum（试卷一/试卷二）
#    - `###` → topic（题型：单选/多选/不定项）
#    - 数字序号 `\d+\.` → 单题开始
#    - `A.` `B.` `C.` `D.` → 选项提取
#    - `**答案：**` 或 `**答案：**` → 答案提取
# 2. 输出 question_import.json（JSON Lines 格式）
```

**支持的 Markdown 格式识别**（从现有文件总结）：

- 标题行：`# 2014年国家司法考试真题（客观题）` → curriculum
- 子标题：`## 试卷一` → subject
- 题型行：`### 一、单项选择题（1-50题，每题1分）` → topic_path
- 题目编号：`1. 题目内容...` → stem 开始
- 选项行：`A. 选项内容` → 存入 options
- 答案行：`**答案：B**` 或 `**答案：B**` → answer

#### Step 2.3 — 批量导入脚本

在 `backend/scripts/` 下创建 `import_questions.py`：

```python
# 读取 question_import.json
# 调用 POST /api/questions 逐个导入
# 支持断点续传（记录已导入的 question_id）
# 支持去重（按 year + paper + number 组合判断）
```

### Phase 3: 前端功能页面

#### Step 3.1 — API 接入层

在 `frontend/lib/` 下创建 `api.ts`，封装所有后端 API 调用。

#### Step 3.2 — 题库查看/分析页面（面向学生/普通用户）

**路径：** `/questions`

功能要求：
- [x] 左侧筛选面板：按 curriculum → subject → type 三级联动筛选
- [x] 右侧题目列表：卡片式展示（题号、题面截取、类型标签）
- [x] 点击卡片 → 弹窗或路由到详情页 `/questions/{id}`
- [x] 详情页展示完整内容：题面、选项（高亮）、答案、解析/题解
- [x] 分页/无限滚动

**页面路由设计：**
```
/questions                     → 列表页（含筛选）
/questions/{id}               → 详情页
```

#### Step 3.3 — 后台管理页面（面向管理员）

**路径：** `/admin/questions`

功能要求：
- [x] 表格展示所有题目（分页）
- [x] 每行可编辑（快速修改 curriculum/subject/type/difficulty）
- [x] 新增题目表单（全字段）
- [x] 删除按钮（需二次确认）
- [x] 批量操作：批量删除、批量修改科目
- [x] 搜索框：支持对 stem 全文搜索

**页面路由设计：**
```
/admin                         → 管理后台首页（含各管理入口）
/admin/questions               → 题目管理列表
/admin/questions/new           → 新增题目
/admin/questions/{id}/edit     → 编辑题目
```

### Phase 4: 部署与测试

1. 运行解析脚本，导入 2014/2020/2021/2022 四套真题
2. 验证前后端数据一致性
3. 测试筛选、搜索、CRUD 功能

---

## 4. 文件变更清单

### 后端新增文件
| 文件 | 用途 |
|------|------|
| `backend/app/routers/questions.py` | Question CRUD API |
| `backend/scripts/parse_fakao.py` | Markdown → JSON 解析器 |
| `backend/scripts/import_questions.py` | JSON → 数据库导入器 |

### 后端修改文件
| 文件 | 变更 |
|------|------|
| `backend/app/main.py` | 注册 `questions.router` |

### 前端新增文件
| 文件 | 用途 |
|------|------|
| `frontend/lib/api.ts` | API 封装 |
| `frontend/app/questions/page.tsx` | 题目浏览列表页 |
| `frontend/app/questions/[id]/page.tsx` | 题目详情页 |
| `frontend/app/admin/page.tsx` | 管理后台首页 |
| `frontend/app/admin/questions/page.tsx` | 题目管理列表 |
| `frontend/app/admin/questions/new/page.tsx` | 新增题目 |
| `frontend/app/admin/questions/[id]/edit/page.tsx` | 编辑题目 |

### 前端修改文件
| 文件 | 变更 |
|------|------|
| `frontend/app/layout.tsx` | 添加导航菜单（首页/题库/管理） |
| `frontend/app/page.tsx` | 更新为仪表盘/入口页 |

---

## 5. 技术选型与依赖

### 后端
- Python 3.11+
- FastAPI + SQLAlchemy 2.0
- Pydantic v2（已有）
- 解析依赖：`python-docx`（如果未来有 .docx 文件）、标准库 `re` / `json`

### 前端
- Next.js 14 App Router（已有）
- Tailwind CSS（已有）
- 无需额外 UI 框架：用 Tailwind + 自定义组件
- 数据获取：原生 `fetch`（无需引入 axios）

---

## 6. 时间估算

| 阶段 | 工作量 | 实际用时（TODO） |
|------|--------|----------------|
| Phase 1: 后端 API | 1~2 天 | |
| Phase 2: 解析脚本 | 1~2 天 | |
| Phase 3: 前端页面 | 2~3 天 | |
| Phase 4: 导入数据 + 测试 | 0.5~1 天 | |
| **合计** | **4.5~8 天** | |

---

## 7. 注意事项

1. **题目去重**：不同年份可能出现相似题目，建议用 `source_origin` 区分来源，不做强去重
2. **答案提取**：部分文件答案格式不统一（`**答案：B**` vs `**答案: B**`），解析脚本需要覆盖所有变体
3. **多项选择题答案**：如 `ABC` 等连续字符串，存入 `answer` 字段
4. **前端无答案模式**：分析页面默认隐藏答案，可通过切换显示/隐藏来控制
5. **分页方案**：后端使用 `limit`/`offset` 分页，前端配合 Next.js 的 searchParams 实现 URL 级分页状态