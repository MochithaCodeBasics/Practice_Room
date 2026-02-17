"use client"
import * as AccordionPrimitive from '@radix-ui/react-accordion'
import { ChevronDown } from 'lucide-react'

export default function AccordionExample() {
  return (
    <div className="p-8 max-w-lg mx-auto">
      <h1 className="title mb-4">Accordion Example</h1>
      <AccordionPrimitive.Root type="single" collapsible className="w-full">
        {[
          {
            id: 'item-1',
            header: 'What is Next.js?',
            content:
              'Next.js is a React framework for building full‑stack web applications. It provides server-side rendering, static site generation and API routes.',
          },
          {
            id: 'item-2',
            header: 'What is shadcn/ui?',
            content:
              'shadcn/ui is an open source library of beautifully designed components built with Radix UI and Tailwind CSS.',
          },
          {
            id: 'item-3',
            header: 'How do I bundle my artifact?',
            content:
              'Run the provided bundle-artifact.sh script from your project root. It builds and exports your Next app, then inlines all assets into a single HTML file.',
          },
        ].map(({ id, header, content }) => (
          <AccordionPrimitive.Item
            key={id}
            value={id}
            className="border-b border-gray-200 dark:border-gray-700"
          >
            <AccordionPrimitive.Header className="py-4">
              <AccordionPrimitive.Trigger
                className="flex w-full items-center justify-between text-left heading hover-underline-animation"
              >
                {header}
                <ChevronDown
                  className="transition-transform data-[state=open]:rotate-180"
                  size={20}
                />
              </AccordionPrimitive.Trigger>
            </AccordionPrimitive.Header>
            <AccordionPrimitive.Content className="accordion-content px-2 pb-4 text-sm prose">
              {content}
            </AccordionPrimitive.Content>
          </AccordionPrimitive.Item>
        ))}
      </AccordionPrimitive.Root>
    </div>
  )
}