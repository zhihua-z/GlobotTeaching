# Frontend — Globot Teaching Next.js App

Next.js 14 frontend for the Globot Teaching platform — a personalised legal exam (法考) preparation platform. Built with the App Router, React 18, TailwindCSS, and shadcn/ui components.

## Tech Stack

| Category       | Technology                                                  |
| -------------- | ----------------------------------------------------------- |
| Framework      | Next.js 14.2 (App Router, `output: "standalone"` for Docker) |
| Language       | TypeScript 5.7                                               |
| UI Library     | React 18.3.1                                                 |
| Styling        | TailwindCSS 3.4 + `tailwindcss-animate`                      |
| Components     | shadcn/ui (via `@radix-ui/react-slot`, `class-variance-authority`) |
| Icons          | lucide-react 0.487                                           |
| State/Data     | TanStack Query (React Query) for client-side data fetching   |
| Forms          | react-hook-form + zod (planned)                              |
| Utility        | clsx, tailwind-merge (via `cn()` helper)                     |
| Build Tooling  | PostCSS 8.5 + autoprefixer                                    |
| Infra          | Docker (multi-stage: deps → builder → runner), Docker Compose |

## Dependencies

### Runtime

| Package                | Version   | Purpose                          |
| ---------------------- | --------- | -------------------------------- |
| next                   | 14.2.29   | Framework (React-based SSR/SSG)  |
| react / react-dom      | ^18.3.1   | UI library                       |
| @radix-ui/react-slot   | ^1.1.2    | Polymorphic component primitive   |
| class-variance-authority | ^0.7.1  | Component variant API            |
| clsx                   | ^2.1.1    | Conditional class joining        |
| lucide-react           | ^0.487.0  | SVG icon library                 |
| tailwind-merge         | ^3.2.0    | Intelligent Tailwind class merging |
| tailwindcss-animate    | ^1.0.7    | Tailwind animation plugin        |
| @tanstack/react-query  | ^5.x      | Server-state management          |

### Dev Dependencies

| Package                | Version   | Purpose                          |
| ---------------------- | --------- | -------------------------------- |
| @types/node            | ^20.17.24 | Node.js type definitions         |
| @types/react           | ^18.3.18  | React type definitions           |
| @types/react-dom       | ^18.3.5   | ReactDOM type definitions        |
| autoprefixer           | ^10.4.21  | CSS vendor prefixing             |
| postcss                | ^8.5.3    | CSS post-processor               |
| tailwindcss            | ^3.4.17   | Utility-first CSS framework      |
| typescript             | ^5.7.3    | TypeScript compiler              |

## Architecture

```
frontend/
├── app/
│   ├── (auth)/login/           # Login page
│   ├── (public)/questions/[id]/ # Public question detail view
│   ├── (student)/              # Student routes (requires auth)
│   │   ├── layout.tsx          # Student sidebar + topbar
│   │   ├── home/               # /home — dashboard landing
│   │   ├── chat/               # /chat — AI 法考对话助手
│   │   ├── practice/           # /practice — practice entry
│   │   ├── practice/[sessionId]/ # /practice/[id] — active session
│   │   ├── review/             # /review — FSRS review cards
│   │   ├── mistakes/           # /mistakes — mistake book
│   │   ├── progress/           # /progress — study progress
│   │   ├── dashboard/          # /dashboard — self-study dashboard
│   │   ├── dashboard/reports/[week]/ # weekly reports
│   │   ├── legal-articles/     # /legal-articles — article lookup
│   │   ├── legal-articles/[id]/# article detail
│   │   └── profile/            # /profile — knowledge graph
│   ├── admin/                  # Admin routes (requires admin role)
│   │   ├── layout.tsx          # Admin topbar + sidebar
│   │   ├── page.tsx            # /admin — admin overview
│   │   ├── questions/          # question CRUD, import, edit
│   │   ├── review/             # review queue for AI-generated drafts
│   │   ├── taxonomy/           # subject & topic management
│   │   ├── legal-articles/     # legal article CRUD
│   │   ├── pipeline/           # pipeline monitoring
│   │   ├── prompts/            # system prompt template management
│   │   └── evals/              # eval set management
│   ├── settings/               # /settings — user settings
│   ├── globals.css             # Tailwind base + shadcn/ui CSS vars
│   ├── layout.tsx              # Root layout (Inter font, providers)
│   ├── middleware.ts           # Route guard (auth + admin check)
│   └── page.tsx                # Landing page
├── components/
│   ├── admin/                  # Admin-specific components
│   │   ├── BulkImportDialog.tsx # Bulk question import dialog
│   │   ├── QuestionFilters.tsx  # Question list filters
│   │   ├── QuestionForm.tsx     # Question create/edit form
│   │   ├── QuestionTable.tsx    # Question data table
│   │   └── TaxonomyTree.tsx     # Subject/topic tree editor
│   ├── question/               # Question display components
│   │   ├── QuestionStem.tsx    # Question stem (markdown + KaTeX)
│   │   ├── OptionsBlock.tsx    # Multiple choice options
│   │   ├── AnswerBlock.tsx     # Correct answer display
│   │   ├── RubricBlock.tsx     # Rubric / marking scheme
│   │   ├── SolutionBlock.tsx   # Solution explanation
│   │   ├── SimilarList.tsx     # Similar questions list
│   │   └── DifficultyChart.tsx # Difficulty breakdown chart
│   └── ui/                     # shadcn/ui primitives
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── progress.tsx
│       ├── scroll-area.tsx
│       ├── select.tsx
│       ├── skeleton.tsx
│       ├── tabs.tsx
│       ├── textarea.tsx
│       ├── toast.tsx
│       ├── toaster.tsx
│       └── use-toast.ts
├── lib/
│   ├── utils.ts                # cn() helper
│   ├── api/
│   │   ├── client.ts           # Axios/fetch wrapper with cookie auth
│   │   ├── mock.ts             # Mock data for development
│   │   ├── questions.ts        # Question API calls
│   │   └── taxonomy.ts         # Taxonomy API calls
│   ├── hooks/
│   │   ├── useQuestions.ts     # TanStack Query hooks for questions
│   │   ├── useQuestionTypes.ts # Question type query hooks
│   │   └── useTaxonomy.ts      # Taxonomy query hooks
│   ├── providers/
│   │   └── QueryProvider.tsx   # TanStack Query provider wrapper
│   └── types/
│       └── api.ts              # API response types
├── src/
│   └── types/
│       └── question.ts         # TypeScript types (mirrors backend schemas)
├── public/
│   └── .gitkeep
├── scripts/
│   └── verify-routes.sh        # Route connectivity validation script
├── Dockerfile
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.mjs
├── tsconfig.json
├── middleware.ts
├── .env.example
└── package.json
```

## Pages — Current Implementation Status

All route pages from the [implementation plan](../docs/implementation-plan/IMPLEMENTATION-PLAN-2-前端页面与后端API总设计.md) have been scaffolded with `page.tsx` files. Below is the status of each page:

### Student Pages

| Route | Status | Description |
| ----- | ------ | ----------- |
| `/` (landing) | ✅ Done | Landing page with "Get Started" / "Learn More" |
| `/home` | ✅ Done | Daily dashboard — review due, recommended practice, gap hints, weekly mini chart, subject progress bars |
| `/chat` | ✅ Done | AI 法考对话助手 — session sidebar, message stream, slash commands |
| `/practice` | ✅ Done | Practice entry — subject/topic/mode selection, history |
| `/practice/[sessionId]` | ✅ Done | Active practice session — question navigation, timer, answer submission |
| `/review` | ✅ Done | FSRS review cards — due queue, rating buttons (Again/Hard/Good/Easy) |
| `/mistakes` | ✅ Done | Mistake book — filterable/sortable list, redo, mark mastered |
| `/progress` | ✅ Done | Subject progress — per-subject bars, current chapter, ETA |
| `/dashboard` | ✅ Done | Self-study dashboard — heatmap, weakness list, trends, countdown |
| `/dashboard/reports/[week]` | ✅ Done | Weekly report detail |
| `/legal-articles` | ✅ Done | Legal article search & browse |
| `/legal-articles/[id]` | ✅ Done | Legal article detail with related questions |
| `/questions/[id]` (public) | ✅ Done | Public question detail & analysis |
| `/profile` | ✅ Done | Personal knowledge graph — L1-L4 profile visualization |

### Admin Pages

| Route | Status | Description |
| ----- | ------ | ----------- |
| `/admin` | ✅ Done | Admin overview — card navigation, key metrics |
| `/admin/questions` | ✅ Done | Question management list with filters |
| `/admin/questions/new` | ✅ Done | Create new question form |
| `/admin/questions/[id]/edit` | ✅ Done | Edit existing question |
| `/admin/questions/import` | ✅ Done | Bulk import (`.jsonl` / `.md` drag & drop) |
| `/admin/review` | ✅ Done | Review queue — AI-generated draft approval workflow |
| `/admin/review/[draftId]` | ✅ Done | Single draft review with keyboard shortcuts |
| `/admin/taxonomy` | ✅ Done | Subject/topic/taxonomy management |
| `/admin/legal-articles` | ✅ Done | Legal article CRUD list |
| `/admin/legal-articles/[id]` | ✅ Done | Legal article detail/edit |
| `/admin/pipeline` | ✅ Done | Pipeline run monitor |
| `/admin/pipeline/[runId]` | ✅ Done | Single run detail with stage breakdown |
| `/admin/prompts` | ✅ Done | System prompt template management |
| `/admin/evals` | ✅ Done | Eval set management & run history |

### Auth & Settings

| Route | Status | Description |
| ----- | ------ | ----------- |
| `/login` | ✅ Done | Email + password login with httpOnly cookie |
| `/settings` | ✅ Done | User settings — study preferences, reminders, data export |

**Total: 33 route files (page.tsx + layout.tsx)**

## Middleware

`middleware.ts` provides route guards:

- Redirects unauthenticated users to `/login` for all student & admin routes
- Redirects non-admin users to `/` for admin routes
- Uses httpOnly cookie-based session validation

## Type Definitions (`src/types/question.ts`)

The frontend maintains type definitions that mirror the backend Pydantic schemas:

- **`QuestionType`** — Union type matching backend enum (multiple_choice, single_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering)
- **`Question`** — Full question object returned from API (id, timestamps, curriculum, subject, topic_path, difficulty, type, stem, options, answer, rubric, solution, variants, source_origin)
- **`QuestionCreate`** — Payload for creating/updating questions
- **`QuestionEmbedding`** — Embedding record with 1024-dim vector array

## Data Fetching

- **Server-side**: React Server Components with server-side fetch via `lib/api/server.ts` (cookie forwarding)
- **Client-side**: TanStack Query hooks in `lib/hooks/` with 60s default staleTime
- **Streaming**: Native `EventSource` for chat & import progress
- **Types**: Auto-generated from FastAPI `/openapi.json` via `openapi-typescript` (planned)

## Configuration

| Variable              | Default                   | Description              |
| --------------------- | ------------------------- | ------------------------ |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`   | Backend API base URL     |

Copy `.env.example` to `.env.local` and adjust as needed:

```bash
cp frontend/.env.example frontend/.env.local
```

## Development

### With Docker

```bash
# From the project root:
docker compose up frontend
# Or all services:
docker compose up --build
```

### Without Docker

```bash
cd frontend
npm install
npm run dev          # → http://localhost:3000

# Production build:
npm run build && npm start
```

## Route Verification

A script is provided to verify connectivity of all routes:

```bash
./frontend/scripts/verify-routes.sh
```

## Build Output

The Next.js config uses `output: "standalone"` which creates a minimal production build in `.next/standalone/`. This is optimized for Docker, including only the necessary runtime files.

## Related Documentation

- [Frontend & Backend API Design](../docs/implementation-plan/IMPLEMENTATION-PLAN-2-前端页面与后端API总设计.md) — Complete page list, layout, and API contract
- [Question Import & Analysis Implementation](../docs/implementation-plan/IMPLEMENTATION-PLAN-1-题库导入+题目分析页+题库管理页.md) — Stage 1 detailed plan