#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------------
# init‑artifact.sh
#
# A script to scaffold a new Next.js project for use with the
# next‑web‑artifacts‑builder skill. It creates a TypeScript‑based app router
# project, installs Tailwind CSS 3.4.1 and shadcn/ui dependencies, and
# applies the provided global styles and theme configuration. After running
# this script you will have a ready‑to‑use Next.js project configured with
# the brand guidelines defined in `globals.css`.
#
# Usage:
#   bash scripts/init‑artifact.sh <project‑name>
#
##############################################################################

# Ensure Node.js ≥ 18 is installed
NODE_VERSION=$(node -v | sed 's/v//' | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Error: Node.js 18 or higher is required"
  echo "   Current version: $(node -v)"
  exit 1
fi

# Determine sed in‑place syntax for macOS vs Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_INPLACE="sed -i ''"
else
  SED_INPLACE="sed -i"
fi

# Ensure pnpm is installed
if ! command -v pnpm >/dev/null 2>&1; then
  echo " pnpm not found. Installing pnpm..."
  npm install -g pnpm
fi

# Validate arguments
if [ $# -lt 1 ]; then
  echo "❌ Usage: $0 <project‑name>"
  exit 1
fi
PROJECT_NAME="$1"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the Next.js app (skip Tailwind because we'll install and configure manually)
echo " Creating new Next.js project: $PROJECT_NAME"
pnpm create next-app "$PROJECT_NAME" -- --ts --app --eslint --tailwind=false --src-dir=false --import-alias "@/*" --use-npm

cd "$PROJECT_NAME"

# Replace npm with pnpm for dependency management
if [ -f package-lock.json ]; then
  rm package-lock.json
fi
if [ -f yarn.lock ]; then
  rm yarn.lock
fi
echo " Installing dependencies..."
pnpm install

# Install Tailwind CSS and other base dependencies
echo " Installing Tailwind CSS and peer dependencies..."
pnpm add -D tailwindcss@3.4.1 postcss autoprefixer

# Install utilities used by shadcn/ui and general component composition
echo " Installing class-variance-authority, clsx and tailwind-merge..."
pnpm add class-variance-authority clsx tailwind-merge

# Install shadcn/ui base dependencies (Radix UI primitives and helpers)
echo " Installing shadcn/ui and Radix dependencies..."
pnpm add @radix-ui/react-accordion @radix-ui/react-aspect-ratio @radix-ui/react-avatar \
  @radix-ui/react-button @radix-ui/react-checkbox @radix-ui/react-collapsible \
  @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-hover-card \
  @radix-ui/react-input @radix-ui/react-label @radix-ui/react-menubar \
  @radix-ui/react-navigation-menu @radix-ui/react-popover @radix-ui/react-progress \
  @radix-ui/react-radio-group @radix-ui/react-scroll-area @radix-ui/react-select \
  @radix-ui/react-separator @radix-ui/react-slider @radix-ui/react-switch \
  @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-toggle \
  @radix-ui/react-tooltip
pnpm add next-themes lucide-react

# Initialize Tailwind configuration files
echo " Creating Tailwind and PostCSS configuration..."
cat > postcss.config.js <<'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

cat > tailwind.config.js <<'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [],
}
EOF

# Create application directories if not present
mkdir -p app
mkdir -p components/ui

# Remove default global CSS and page files created by create-next-app
rm -f app/globals.css || true
rm -f app/page.tsx || true

# Copy the provided globals.css into the project
echo " Adding brand global styles..."
cat > app/globals.css <<'EOF'
@import 'tailwindcss';

@theme {
  --breakpoint-phone: 380px;
  --breakpoint-phablet: 550px;
  --breakpoint-tablet: 640px;
  --breakpoint-tabletpro: 768px;
  --breakpoint-laptop: 1024px;
  --breakpoint-desktop: 1280px;

  /* Font */
  --font-manrope: 'Manrope', sans-serif;

  /* Colors */
  --color-bg: #ffffff;
  --color-text: #0f172a;
  --color-muted: #64748b;
  --color-link: #1d4ed8;

  --color-bg--dark: #0b0f19;
  --color-text--dark: #e5e7eb;
  --color-muted--dark: #9ca3af;
  --color-link--dark: #60a5fa;

  --color-primary-btn-color: #3b82f6;
  --color-primary-btn-hover-color: #2474f5;
  --color-primary-btn-active-color: #0a5adb;

  --color-secondary-btn-color: #ebf2ff;

  --color-primaryBlack: #000000;
  --color-secondaryBlack: #3e4143;

  --color-primaryWhite: #ffffff;

  --color-defaultBlue: #3b82f6;
  --color-secondaryBlue: #dbeafe;

  --color-filterButton: #d9d9d9;

  --color-primaryGray: #616161;
  --color-secondaryGray: #a1a1a1;
  --color-bgSecondaryGray: #fbfbfb;
  --color-shimmerGray: #d9d9d9;

  --color-subheading-color: #616161;

  --color-primaryGrayBorder: #d1d5db;

  --color-text-gray-color: #616161;

  --color-primaryGreen: #28d26a;
  --color-secondaryGreen: #d1fae5;

  --color-primaryBlueBackground: #f7faff;

  --text-display: 48px;
  --text-title: 36px;
  --text-subtitle: 24px;
  --text-heading: 20px;
  --text-subheading: 18px;
  --text-paragraph: 16px;
  --text-micro: 14px;
  --text-nano: 12px;

  --leading-tight: 1.2;
  --leading-snug: 1.35;
  --leading-normal: 1.55;
  --leading-loose: 1.75;

  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --weight-extrabold: 800;

  --tracking-tight: -0.01em;
  --tracking-normal: 0;
}

html,
body {
  font-family: var(--font-manrope);
  height: 100%;
}

button {
  cursor: pointer;
}

link {
  cursor: pointer;
}

.display {
  font-family: var(--font-manrope);
  font-size: clamp(32px, 3.428571vw, var(--text-display));
  line-height: var(--leading-tight);
  font-weight: var(--weight-extrabold);
  letter-spacing: var(--tracking-tight);
}

.title {
  font-family: var(--font-manrope);
  font-size: clamp(24px, 2.428571vw, var(--text-title));
  line-height: var(--leading-tight);
  font-weight: var(--weight-bold);
}

.subtitle {
  font-family: var(--font-manrope);
  font-size: clamp(20px, 1.714286vw, var(--text-subtitle));
  line-height: var(--leading-tight);
  font-weight: var(--weight-bold);
}

.heading {
  font-family: var(--font-manrope);
  font-size: clamp(16px, 1.428571vw, var(--text-heading));
  line-height: var(--leading-snug);
  font-weight: var(--weight-bold);
}

.subheading {
  font-family: var(--font-manrope);
  font-size: clamp(15px, 1.285714vw, var(--text-subheading));
  line-height: var(--leading-snug);
  font-weight: var(--weight-medium);
}

.paragraph {
  font-family: var(--font-manrope);
  font-size: clamp(13px, 1.142857vw, var(--text-paragraph));
  line-height: var(--leading-normal);
  font-weight: var(--weight-regular);
}

.small {
  font-family: var(--font-manrope);
  font-size: clamp(12px, 1.142857vw, var(--text-micro));
  line-height: var(--leading-normal);
  font-weight: var(--weight-semibold);
}

.nanoText {
  font-family: var(--font-manrope);
  font-size: clamp(10px, 1.142857vw, var(--text-nano));
  line-height: var(--leading-normal);
  font-weight: var(--weight-semibold);
}

.subheadingColor {
  color: var(--color--subheading-color);
}

.grayTextColor {
  color: var(--color--text-gray-color);
}

.muted {
  color: var(--color-muted);
}

.eyebrow {
  font-family: var(--font-manrope);
  font-size: var(--text-micro);
  line-height: var(--leading-normal);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.lead {
  font-family: var(--font-manrope);
  font-size: var(--text-subtitle);
  line-height: var(--leading-loose);
  font-weight: var(--weight-regular);
}

.primaryBtnShine {
  background-color: var(--color-primary-btn-color);
  color: var(--color-primaryWhite);
  font-weight: var(--weight-medium);
  font-size: var(--text-paragraph);
}

.primaryBtnShine:hover {
  background-color: var(--color-primary-btn-hover-color);
}

.primaryBtnShine:active {
  background-color: var(--color-primary-btn-active-color);
}

.secondaryBtn {
  background-color: var(--color-secondary-btn-color);
  color: var(--color-defaultBlue);
  font-weight: var(--weight-medium);
  font-size: var(--text-paragraph);
}

.link {
  color: var(--color-link);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.dark .display,
.dark .title,
.dark .subtitle,
.dark .heading,
.dark .subheading,
.dark .paragraph,
.dark .small,
.dark .muted,
.dark .eyebrow,
.dark .lead {
  color: var(--color-text--dark);
}

.dark .small,
.dark .muted,
.dark .eyebrow {
  color: var(--color-muted--dark);
}

.dark .link {
  color: var(--color-link--dark);
}

.bg-card-container {
  background-color: #f7faff;
}

.animate-slide-in {
  animation: slide-in 0.7s ease-out forwards;
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition:
    max-height 0.3s ease-in-out,
    opacity 0.3s ease-in-out;
}

.accordion-content.open {
  max-height: 500px;
  opacity: 1;
}

@keyframes slide-in {
  0% {
    transform: translateY(100%);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.prose ul,
.prose ol {
  list-style: initial;
  margin-left: 1.2rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-left: 0;
}

.prose a {
  color: #1d4ed8;
  text-decoration: none;
  transition: text-decoration 0.2s;
}

.prose a:hover {
  text-decoration: underline;
}

.glass-shine {
  position: relative;
  overflow: hidden;
}

.glass-shine::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0) 40%,
      rgba(255, 255, 255, 0.4) 50%,
      rgba(255, 255, 255, 0) 60%);
  transform: rotate(0deg);
  animation: glass-shine-move 4s linear infinite;
  pointer-events: none;
}

@keyframes glass-shine-move {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  100% {
    transform: translate(50%, 50%) rotate(0deg);
  }
}

.hover-underline-animation {
  position: relative;
  transition: color 0.5s;
}

.hover-underline-animation::before {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 0;
  height: 2px;
  background-color: #2563eb;
  transition: width 0.3s ease;
}

.hover-underline-animation:hover {
  color: #2563eb;
}

.hover-underline-animation:hover::before {
  width: 100%;
}

.hover-underline-animation:focus-visible {
  color: #2563eb;
}

.hover-underline-animation:focus-visible::before {
  width: 100%;
}
EOF

# Write default layout.tsx file
echo " Creating Next.js layout and page..."
cat > app/layout.tsx <<'EOF'
import './globals.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'Next Web Artifact',
  description: 'A starter template for creating web artifacts with Next.js and shadcn/ui',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-slate-900 dark:bg-zinc-900 dark:text-slate-50">
        {children}
      </body>
    </html>
  )
}
EOF

# Write sample page.tsx using shadcn/ui style button
cat > app/page.tsx <<'EOF'
import { useState } from 'react'

export default function Home() {
  const [count, setCount] = useState(0)
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <h1 className="display text-center">Welcome to your Next Web Artifact</h1>
      <p className="paragraph text-center max-w-prose">
        This starter project was created by the next-web-artifacts-builder skill. It includes
        Tailwind CSS configured with a custom design system and shadcn/ui dependencies.
        Edit <code className="bg-gray-100 px-1 rounded">app/page.tsx</code> to start building
        your artifact.
      </p>
      <button
        onClick={() => setCount((c) => c + 1)}
        className="primaryBtnShine px-5 py-2 rounded-md hover:shadow-lg transition"
      >
        You clicked {count} time{count === 1 ? '' : 's'}
      </button>
    </main>
  )
}
EOF

# Create a basic TypeScript config if not present
if [ ! -f tsconfig.json ]; then
  cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "es2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "types": ["node"],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
EOF
fi

echo "✅ Setup complete! Your Next.js project is ready."
echo "   To start developing, run: pnpm run dev"
echo "   When finished, bundle your artifact with: bash ../scripts/bundle-artifact.sh"