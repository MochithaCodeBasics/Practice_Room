import { useState } from 'react'

export default function Home() {
  const [count, setCount] = useState(0)
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <h1 className="display text-center">Welcome to your Next Web Artifact</h1>
      <p className="paragraph text-center max-w-prose">
        This starter template includes Tailwind CSS configured with a custom design system
        and all dependencies needed to use shadcn/ui. You can start building your
        claude.ai artifact right away.
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