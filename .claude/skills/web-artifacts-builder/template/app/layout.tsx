import './globals.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'Next Web Artifact Template',
  description: 'A minimal starting point for building claude.ai HTML artifacts with Next.js',
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