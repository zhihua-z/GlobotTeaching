# Contributing to GlobotTeaching

## Project Structure Overview

This project is a monorepo containing a **FastAPI backend** (Python) and a **Next.js frontend** (TypeScript) for a legal exam preparation platform (法考客观题).

```
GlobotTeaching/
├── backend/                 # FastAPI (Python) backend
├── frontend/                # Next.js (TypeScript) frontend
├── data/                    # Raw data files (drafts in JSONL)
├── docs/                    # Documentation
├── docker-compose.yml       # Docker orchestration
└── .github/                 # GitHub configuration
```

---

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Application configuration
│   ├── database.py              # Database session management
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py              # Declarative base
│   │   ├── question.py          # Question model
│   │   ├── taxonomy.py          # Taxonomy model
│   │   ├── embedding.py         # Embedding model
│   │   ├── question_embedding.py
│   │   └── document.py          # Legal document model
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── question.py
│   │   └── taxonomy.py
│   ├── routers/                 # API route handlers
│   │   ├── questions.py         # /api/questions/*
│   │   ├── taxonomy.py          # /api/taxonomy/*
│   │   ├── analysis.py          # /api/analysis/*
│   │   ├── health.py            # Health check
│   │   └── question_types.py    # Question type metadata
│   ├── services/                # Business logic layer
│   │   ├── question_service.py
│   │   ├── analysis_service.py
│   │   └── llm.py               # LLM integration
│   └── repositories/            # Data access layer
│       ├── question_repo.py
│       └── taxonomy_repo.py
├── scripts/
│   └── ingest/                  # Data ingestion pipeline
│       ├── parse_pdf.py
│       ├── parse_docx.py
│       ├── parse_markdown.py
│       ├── parse_fakao_markdown.py
│       ├── normalize.py
│       ├── embed_worker.py
│       ├── classify.py
│       ├── seed_questions.py
│       └── seed_taxonomy.py
├── alembic/                     # Database migrations
│   └── versions/
│       ├── 0001_create_questions_and_embeddings.py
│       ├── 0002_add_taxonomy.py
│       └── 0003_add_indexes.py
├── tests/
│   ├── test_ingest_pipeline.py
│   ├── test_questions_router.py
│   └── test_taxonomy_router.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## Frontend Structure (`frontend/`)

### Next.js App Router Conventions

The frontend uses **Next.js App Router** with the following route group conventions:

| Route Group     | Purpose                          |
|-----------------|----------------------------------|
| `(auth)`        | Authentication pages (login)     |
| `(public)`      | Publicly accessible pages        |
| `(student)`     | Student-facing (requires auth)   |
| `admin`         | Admin pages (requires admin)     |
| `settings`      | User settings                    |

### Routing Table

| URL Path                                   | File Path                                                    | Description                     |
|--------------------------------------------|--------------------------------------------------------------|---------------------------------|
| `/login`                                   | `app/(auth)/login/page.tsx`                                  | Login page                      |
| `/questions/[id]`                          | `app/(public)/questions/[id]/page.tsx`                       | Public question detail          |
| `/`                                        | `app/page.tsx`                                               | Landing page                    |
| `/dashboard`                               | `app/(student)/dashboard/page.tsx`                           | Student dashboard               |
| `/dashboard/reports`                       | `app/(student)/dashboard/reports/page.tsx`                   | Student reports                 |
| `/home`                                    | `app/(student)/home/page.tsx`                                | Student home                    |
| `/chat`                                    | `app/(student)/chat/page.tsx`                                | Chat/assistant                  |
| `/practice`                                | `app/(student)/practice/page.tsx`                            | Practice overview               |
| `/practice/[sessionId]`                    | `app/(student)/practice/[sessionId]/page.tsx`                | Practice session                |
| `/mistakes`                                | `app/(student)/mistakes/page.tsx`                            | Mistake review                  |
| `/review`                                  | `app/(student)/review/page.tsx`                              | Review page                     |
| `/progress`                                | `app/(student)/progress/page.tsx`                            | Progress tracking               |
| `/profile`                                 | `app/(student)/profile/page.tsx`                             | User profile                    |
| `/legal-articles`                          | `app/(student)/legal-articles/page.tsx`                      | Legal articles list             |
| `/legal-articles/[id]`                     | `app/(student)/legal-articles/[id]/page.tsx`                 | Legal article detail            |
| `/admin`                                   | `app/admin/page.tsx`                                         | Admin dashboard                 |
| `/admin/questions`                         | `app/admin/questions/page.tsx`                               | Admin question management       |
| `/admin/taxonomy`                          | `app/admin/taxonomy/page.tsx`                                | Admin taxonomy management       |
| `/admin/evals`                             | `app/admin/evals/page.tsx`                                   | Admin evaluations               |
| `/admin/review`                            | `app/admin/review/page.tsx`                                  | Admin review queue              |
| `/admin/legal-articles`                    | `app/admin/legal-articles/page.tsx`                          | Admin legal articles list       |
| `/admin/legal-articles/[id]`               | `app/admin/legal-articles/[id]/page.tsx`                     | Admin legal article detail      |
| `/admin/pipeline/[runId]`                  | `app/admin/pipeline/[runId]/page.tsx`                        | Admin pipeline run detail       |
| `/admin/prompts`                           | `app/admin/prompts/page.tsx`                                 | Admin prompt management         |
| `/settings`                                | `app/settings/page.tsx`                                      | User settings                   |

### Frontend Paths & Conventions

To add a new page, follow these conventions:

1. **Route Groups** — Wrap related routes in parentheses `(group)` to organize without affecting the URL path.
2. **Dynamic Routes** — Use square brackets `[param]` for dynamic segments (e.g., `[sessionId]`, `[id]`).
3. **Layouts** — Add a `layout.tsx` in a route group to apply a shared layout (e.g., `app/(student)/layout.tsx`).
4. **Page Files** — Each route must have a `page.tsx` file exporting a React component.

### Component Structure

```
frontend/components/
├── admin/                    # Admin-specific components
│   ├── BulkImportDialog.tsx
│   ├── QuestionFilters.tsx
│   ├── QuestionForm.tsx
│   ├── QuestionTable.tsx
│   └── TaxonomyTree.tsx
├── question/                 # Question-display components
│   ├── AnswerBlock.tsx
│   ├── DifficultyChart.tsx
│   ├── OptionsBlock.tsx
│   ├── QuestionStem.tsx
│   ├── RubricBlock.tsx
│   ├── SimilarList.tsx
│   └── SolutionBlock.tsx
└── ui/                       # Reusable UI primitives (shadcn/ui)
    ├── badge.tsx
    ├── button.tsx
    ├── card.tsx
    ├── dialog.tsx
    ├── input.tsx
    ├── label.tsx
    ├── progress.tsx
    ├── scroll-area.tsx
    ├── select.tsx
    ├── skeleton.tsx
    ├── tabs.tsx
    ├── textarea.tsx
    ├── toast.tsx
    ├── toaster.tsx
    └── use-toast.ts
```

### Lib & API Structure

```
frontend/lib/
├── utils.ts                  # Utility functions (cn, etc.)
├── api/
│   ├── client.ts             # Axios/fetch API client
│   ├── mock.ts               # Mock data for development
│   ├── questions.ts          # Question API calls
│   └── taxonomy.ts           # Taxonomy API calls
├── hooks/
│   ├── useQuestions.ts       # React Query hooks for questions
│   ├── useQuestionTypes.ts   # React Query hooks for question types
│   └── useTaxonomy.ts        # React Query hooks for taxonomy
├── providers/
│   └── QueryProvider.tsx     # TanStack Query provider setup
└── types/
    ├── api.ts                # Shared API response types
    └── question.ts           # Question-specific types
```

### Type Definitions

```
frontend/src/
└── types/
    └── question.ts           # Additional question type definitions
```

### Adding a New Frontend Route — Step-by-Step

1. Determine the route group: `(auth)`, `(public)`, `(student)`, or `admin`.
2. Create the directory under `app/<route-group>/<your-route>/`.
3. Add a `page.tsx` file exporting your default React component.
4. If the route needs a dynamic segment, use `[paramName]` in the directory name.
5. If nesting under a layout is needed, ensure a `layout.tsx` exists in the parent group.
6. Add API calls in `lib/api/` if new endpoints are required.
7. Add React Query hooks in `lib/hooks/` for data fetching.

---

## Data Directory

```
data/
└── drafts/                   # Raw question draft JSONL files
    ├── 2014.jsonl
    ├── 2020.jsonl
    ├── 2021.jsonl
    └── 2022.jsonl
```

## Documentation

```
docs/
├── README.md
├── 2014年法考客观题真题.md
├── 2020年法考客观题真题.md
├── 2021年法考客观题真题.md
├── 2022年法考客观题真题.md
├── 题目分析(deepseek)implementation_plan.md
└── implementation-plan/
    ├── IMPLEMENTATION-PLAN-1-题库导入+题目分析页+题库管理页.md
    └── IMPLEMENTATION-PLAN-2-前端页面与后端API总设计.md