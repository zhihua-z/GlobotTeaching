# Frontend — Globot Teaching Next.js App

Next.js 14 frontend for the Globot Teaching platform, built with the App Router, React 18, TailwindCSS, and shadcn/ui components.

## Tech Stack

| Category       | Technology                                                  |
| -------------- | ----------------------------------------------------------- |
| Framework      | Next.js 14.2 (App Router, `output: "standalone"` for Docker) |
| Language       | TypeScript 5.7                                               |
| UI Library     | React 18.3.1                                                 |
| Styling        | TailwindCSS 3.4 + `tailwindcss-animate`                      |
| Components     | shadcn/ui (via `@radix-ui/react-slot`, `class-variance-authority`) |
| Icons          | lucide-react 0.487                                           |
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
│   ├── globals.css       # Tailwind base + shadcn/ui CSS variables (light/dark)
│   ├── layout.tsx        # Root layout (Inter font, metadata)
│   └── page.tsx          # Home page (landing with "Get Started" / "Learn More")
├── components/
│   └── ui/
│       └── button.tsx    # shadcn/ui Button (variants: default, destructive, outline, secondary, ghost, link; sizes: default, sm, lg, icon)
├── lib/
│   └── utils.ts          # cn() helper — clsx + tailwind-merge
├── src/
│   └── types/
│       └── question.ts   # TypeScript types mirroring backend Question + Embedding schemas
├── public/
│   └── .gitkeep
├── Dockerfile            # Multi-stage build (deps → builder → runner)
├── next.config.mjs       # output: "standalone" for Docker optimization
├── tailwind.config.ts    # Custom theme (border, input, background, foreground, primary, etc.)
├── postcss.config.mjs    # PostCSS with tailwindcss + autoprefixer
├── tsconfig.json         # TypeScript config (bundler module resolution, @/ path alias)
├── .env.example          # NEXT_PUBLIC_API_URL
└── package.json
```

### Component Tree (Current)

```
RootLayout
└── Home (landing page)
    ├── h1 "Globot Teaching"
    ├── p  "AI-powered teaching platform"
    └── div.flex
        ├── Button (primary) "Get Started"
        └── Button (outline) "Learn More"
```

### Type Definitions (`src/types/question.ts`)

The frontend maintains type definitions that mirror the backend Pydantic schemas:

- **`QuestionType`** — Union type matching backend enum (multiple_choice, single_choice, true_false, fill_blank, short_answer, essay, code, matching, ordering)
- **`Question`** — Full question object returned from API (id, timestamps, curriculum, subject, topic_path, difficulty, type, stem, options, answer, rubric, solution, variants, source_origin)
- **`QuestionCreate`** — Payload for creating/updating questions
- **`QuestionEmbedding`** — Embedding record with 1024-dim vector array

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

## Build Output

The Next.js config uses `output: "standalone"` which creates a minimal production build in `.next/standalone/`. This is optimized for Docker, including only the necessary runtime files.

## Planned Pages / Features

Based on the documentation (`docs/题目分析(deepseek)implementation_plan.md`), the following features are planned:

- **Question Analysis Page**: View individual question details with full context
- **Admin Panel**: CRUD management for questions, subjects, and types
- **Search**: Vector-similarity-based question search
- **Exam Paper Import**: Parse and display exam papers from structured data