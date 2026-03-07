---
name: next-web-artifacts-builder
description: >
  Suite of tools for creating rich claude.ai HTML artifacts using Next.js, Tailwind
  CSS and shadcn/ui. Choose this skill when you want to build multi‑page or
  stateful web artifacts that go beyond a single HTML file. It scaffolds a new
  Next.js project configured with TypeScript, Tailwind CSS, the shadcn/ui
  component library and the provided brand guidelines. A second script bundles
  the finished app into a single, shareable HTML file.
license: Complete terms in LICENSE.txt
---

# Next Web Artifacts Builder

This skill helps you build sophisticated front‑end web artifacts using **Next.js**,
**Tailwind CSS** and **shadcn/ui**. It is intended for projects that need
multiple pages, routing, or complex UI state. For simple single‑file artifacts,
prefer an inline HTML/JSX approach.

## Quick start

1. Run the initialization script to generate a fresh Next.js project:

   ```bash
   bash scripts/init‑artifact.sh <project‑name>
   cd <project‑name>
   ```

   The script uses `pnpm create next-app` under the hood, installs Tailwind
   CSS 3.4.1, sets up the shadcn/ui dependencies and copies the provided
   `globals.css` stylesheet containing all brand variables and typography
   utilities. Your new project will be ready to develop immediately.

2. Develop your artifact by editing the generated files. The default template
   includes a simple page using Tailwind classes and one shadcn/ui button as
   an example. See the `docs` folder for common development tips.

3. Bundle the Next app into a single HTML file using:

   ```bash
   bash scripts/bundle‑artifact.sh
   ```

   This script runs `next build` and `next export` to produce a static site in
   the `out/` directory. It then uses `html-inline` to inline all CSS and
   JavaScript into a single `bundle.html` file. The resulting file is
   self‑contained and can be shared directly in a Claude conversation.

4. Share the generated `bundle.html` file with the user.

## Design & Style Guidelines

The provided `globals.css` defines a design system aligned with the brand
guidelines. Key points:

- Responsive breakpoints from phones up to desktop sizes.
- A single Manrope font family with multiple weights.
- A comprehensive colour palette with light and dark mode variants.
- Typography utility classes (`display`, `title`, `subtitle`, etc.) with
  predefined font sizes, weights and line heights.
- Button and link styles, accordion animations and glass‑shine effects.

When building your artifact, **avoid common AI design pitfalls** such as
excessive centred layouts, purple gradients, uniform rounded corners and the
Inter font. Use Tailwind’s utility classes in conjunction with the CSS
variables to construct layouts that respect the palette and typography.

## Reference

- **Next.js documentation**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **shadcn/ui components**: https://ui.shadcn.com/docs/components