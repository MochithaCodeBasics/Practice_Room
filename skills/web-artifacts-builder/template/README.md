# Template for Next Web Artifacts Builder

This folder contains a minimal Next.js project preconfigured with the same
structure produced by the `init‑artifact.sh` script. It exists for users who
prefer to start from a static template instead of running the initialization
script. To use it, copy the contents of this folder into your own project
directory, install the dependencies listed in `package.json` with pnpm, and
start the development server.

Files included:

- `app/` – The app router directory containing `layout.tsx`, `page.tsx` and
  the global stylesheet.
- `tailwind.config.js` and `postcss.config.js` – Configuration files for
  Tailwind CSS.
- `tsconfig.json` – A basic TypeScript configuration with a path alias for
  `@/*`.

You will still need to install `tailwindcss@3.4.1`, `postcss`, `autoprefixer`,
`class-variance-authority`, `clsx`, `tailwind-merge`, the Radix UI packages
listed in the skill documentation and `next-themes`. The `init‑artifact.sh`
script handles this automatically.