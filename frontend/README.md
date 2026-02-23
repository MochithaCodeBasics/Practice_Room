# Practice Room - Frontend

Next.js application providing the interactive UI for the Practice Room coding platform.

## Prerequisites

- Node.js v18+
- Backend server running on port 3001

## Setup

```bash
npm install

# Start development server
npm run dev
```

The app runs on **http://localhost:3000**. API requests to `/api/*` are proxied to the backend at `http://localhost:3001`.

## Environment Variables

Configure in `.env.local`:

| Variable | Description |
|----------|-------------|
| `AUTH_SECRET` | NextAuth session secret |
| `AUTH_CODEBASICS_ID` | OAuth client ID |
| `AUTH_CODEBASICS_SECRET` | OAuth client secret |
| `CODEBASICS_BASE_URL` | OAuth provider base URL |
| `NEXT_PUBLIC_APP_URL` | Public app URL (default: `http://localhost:3000`) |
| `BACKEND_URL` | Backend API URL (default: `http://localhost:3001`) |

## Key Features

- **Monaco Editor** — Full-featured Python code editor
- **Run Code** — Execute code and see output instantly
- **Submit & Validate** — Submit solutions for validation against test cases (requires sign-in)
- **Progress Tracking** — Visual indicators (green checkmark) for completed questions
- **Resizable Panels** — Adjustable layout for question details, editor, and console
- **PDF Export** — Download problem + solution as PDF report

## Project Structure

```
frontend/
├── app/                    # Next.js app router pages
│   ├── page.tsx            # Home (module list)
│   ├── modules/[slug]/     # Module question list & workspace
│   ├── admin/              # Admin dashboard
│   └── api/auth/           # NextAuth routes
├── components/             # React components
│   ├── Workspace.tsx       # Main code editor workspace
│   ├── QuestionList.tsx    # Question list with status badges
│   ├── ModuleList.tsx      # Module cards
│   └── AuthPopup.tsx       # Authentication dialog
├── services/api.ts         # API client functions
├── context/AuthContext.tsx  # Auth context provider
├── auth.ts                 # NextAuth configuration
└── middleware.ts           # Auth token injection middleware
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run start` | Run production build |
| `npm run lint` | Lint the project |
