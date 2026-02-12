# Practice Room – Next.js Frontend

This is the **Next.js 15 (App Router)** frontend for the Practice Room app, using **shadcn/ui** components.

## Prerequisites

- **Node.js** 18+ (20.x recommended)
- **npm** or **pnpm**
- Backend running (FastAPI on port 8000) for full functionality

## First-time setup

### 1. Install dependencies

From the root folder:

```bash
cd frontend
npm install
```

### 2. Add logo and assets

Copy your logos and images into the `public/assets` folder:

Required files:

- **logo.png** – used on login, signup, forgot/reset password, admin login, sidebar, and workspace header.
- **python.png** – used in the Workspace code editor header (Python badge).
- **favicon.png** – optional; browser tab icon.

After copying, you should have:

- `frontend/public/assets/logo.png`
- `frontend/public/assets/python.png`
- `frontend/public/assets/favicon.png` (optional)

See `frontend/public/assets/README.md` for details.

## Running the app

### Option A: Run frontend and backend together (recommended)

From the **root** folder:

```bash
start_app.bat
```

This starts:

1. **Backend** – FastAPI at http://localhost:8000  
2. **Frontend** – Next.js at http://localhost:3000  

Then open **http://localhost:3000** in your browser.

### Option B: Run frontend only (backend must already be running)

```bash
cd frontend
npm run dev
```

Open http://localhost:3000. Ensure the FastAPI backend is running on port 8000.

### Build for production

```bash
cd frontend
npm run build
npm start
```

## Tech stack

- **Next.js 15** (App Router)
- **React 18**
- **Tailwind CSS** + **shadcn/ui**
- **Axios** for API calls
- **Monaco Editor**
- **react-markdown**
- **html2pdf.js**

## API connection

The app expects the backend at **http://localhost:8000**. Next.js rewrites `/api/*` to `http://localhost:8000/api/*` (see `next.config.js`).

## Project structure (main parts)

```
frontend/
├── app/
│   ├── layout.jsx           # Root layout + AuthProvider
│   ├── page.jsx              # Redirects to /login
│   ├── login/page.jsx
│   ├── signup/page.jsx
│   ├── forgot-password/page.jsx
│   ├── reset-password/page.jsx
│   ├── admin/login/page.jsx
│   ├── dashboard/            # Protected
│   │   ├── layout.jsx        # ProtectedRoute wrapper
│   │   └── page.jsx
│   └── admin/
│       ├── upload/           # Protected, admin only
│       └── edit/[questionId]/
├── components/
│   ├── ui/                   # shadcn components
│   ├── Layout.jsx
│   ├── ProtectedRoute.jsx
│   ├── Workspace.jsx         # Monaco via dynamic import
│   ├── ModuleList.jsx
│   ├── QuestionList.jsx
│   ├── StreakIndicator.jsx
│   └── UserProfile.jsx
├── context/
│   └── AuthContext.jsx
├── services/
│   └── api.js
├── public/
│   └── assets/               # Put logo.png, python.png here
└── next.config.js            # Rewrites /api -> backend:8000
```
