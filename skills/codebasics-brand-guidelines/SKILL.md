---
name: codebasics-brand-guidelines
description: >
  Applies Codebasics brand identity (voice + visual system) to any digital artifact.
  Use this skill whenever outputs must follow Codebasics rules: dark-first palette,
  Saira Condensed + Kanit typography, logo/badge placement, and gimmick-free copy.
license: Complete terms in LICENSE.txt
---

# Codebasics Brand Guidelines Skill

## Overview

This skill encodes Codebasics brand rules so artifacts look and read like Codebasics.
It covers:

- **Visual identity**: dark-first backgrounds, official palette, gradients, card styling.
- **Typography**: Saira Condensed for headlines, Kanit for body and UI text.
- **Copy & tone**: Sage-first (no fluff, radical honesty), Jester as controlled spice.
- **Templates**: ad creative structure, thumbnail rules, trust signals, “AtliQ standard”.

Use this skill for **presentations, one-pagers, landing pages, social creatives, thumbnails, email templates, dashboards, diagrams**, and any artifact requiring Codebasics consistency.

**Keywords**: codebasics, branding, visual identity, dark theme, Saira Condensed, Kanit, gimmick-free, cinematic, AtliQ

---

## Brand Essence

### About
Codebasics is a **data and AI education company** focused on practical, project-based learning with real outcomes.

- **Purpose**: Learn through easy explanations and upskill for today’s job market.
- **Tagline**: **Enabling Careers**

### Positioning
For **driven aspirants** who want project-based learning, Codebasics is the **gimmick-free education platform** that makes learners job-ready because it’s built by **industry experts** who simplify complex topics.

### Values
- **Easy Explanations**: complex concepts, simple words
- **Gimmick-Free**: no manipulation, no fake urgency
- **Affordable**: premium education shouldn’t cost a fortune
- **Relatable**: speak the learner’s language

---

## Brand Voice

### Core Voice: Sage (80%)
- Senior engineer mentor energy: realistic, data-driven, direct.
- **Rules**:
  - No fluff.
  - Radical honesty: no “instant results”.
  - Anti-salesy: no desperation, no hype.
  - Empowering: assume audience is smart.

### Secondary Voice: Jester (20%)
- Insider humor + self-aware reality checks.
- **Rules**:
  - Joke about pain points (tool fatigue, tutorial hell, Excel crashing).
  - Mock bad habits and fake gurus; **never mock the learner**.
  - Humor must not reduce clarity or trust.

### Language Rules
- Prefer **Learner / Aspirant** over “user/student”.
- Prefer **Investment** over “cost/price”.
- Prefer **Program / Bootcamp** over “course” (for bootcamps).
- Never use: “Free”, “Discount”, “Sale” in marketing contexts.
- Never use fake urgency (“Only 3 seats left!”), strikethrough pricing, salary guarantees.

---

## Visual Identity

### Color System

#### Primary Colors
Use these as the structural palette.

- **Brand Blue (Primary Accent / Logo / CTAs)**: `#3B82F6`
- **Brand Purple (Secondary Accent)**: `#6F53C1`
- **Slate Blue (Muted Mid-tone)**: `#3F4C78`
- **Deep Navy (Primary Background / Dark Mode)**: `#181830`
- **White (Primary Text on Dark)**: `#FFFFFF`

#### Secondary Colors (Use Sparingly)
- **Lime Yellow (High-impact accent)**: `#D7EF3F`
  - Rule: **ONE accent word or short phrase per creative**.
  - Also used for CTA buttons on dark backgrounds.
- **Teal Green (Positive/success states, “alive” elements)**: `#20C997`
- **Orange (Alerts / warm emphasis)**: `#FD7E15`
- **Pink (Occasional accent)**: `#D63384`
- **Light Lavender (Soft background / card fill)**: `#E1E3FA`

#### Colors Not to Use
- Gold/yellow variants outside palette (e.g. `#f0c040`).
- Neon green variants (e.g. `#c7f464`).
- Light/pastel backgrounds as **primary** backgrounds.
- Random greens: use only `#20C997` (teal) or `#D7EF3F` (lime).

### Backgrounds

#### Default Background
- Use **Deep Navy** `#181830` as the default background.

#### Marketing Gradient (Ads)
Use the official gradient for paid ad templates:

```css
background: linear-gradient(
  170deg,
  #0c1630 0%,
  #151040 35%,
  #1a1545 55%,
  #12103a 80%,
  #0c1630 100%
);
```

### Card Styling (Dark UI)

```css
background: rgba(255, 255, 255, 0.03);
border: 1px solid rgba(255, 255, 255, 0.06);
border-radius: 8px;
```

Guideline: cards should feel like a **dark IDE UI**: subtle borders, low-contrast fills, clean spacing.

---

## Typography

### Fonts
- **Headlines / Titles**: **Saira Condensed** (weights 600–900)
- **Body / UI / Labels**: **Kanit** (weights 300–600)

Google Fonts import:

```html
<link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;600;700;800;900&family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">
```

### Hierarchy (Default)
Use this mapping unless a medium-specific section overrides it.

- **Hero headline**: Saira Condensed 900 (Black), uppercase, tight line height.
- **Section headline**: Saira Condensed 700–800.
- **Subheadline**: Kanit 300–400.
- **Body**: Kanit 300–400.
- **Pills / badges**: Kanit 500.
- **Numbers / stats**: Saira Condensed 800.

### Font Color Assignments (Canonical)
- **Title 1**: Saira + `#D7EF3F` (lime)
- **Title 2**: Saira + `#20C997` (teal)
- **Body**: Kanit + `#3B82F6` (blue)
- **Accent**: `#3F4C78` (slate)

Rule: do not rainbow text. Use one dominant text color per block; lime is an accent, not a paragraph color.

---

## Layout Rules by Medium

### Website
- Full palette allowed.
- Default background: `#181830`.
- Blue + purple for trust/structure; lime reserved for **single spotlight**.

### Presentations / Decks
- Simplified palette: **Blue, Teal, Lime, Purple + Slate, Navy**.
- Prefer large Saira headlines + minimal Kanit body.
- Charts: highlight series with Blue/Teal; use Slate for grids/axes.

### Social Creatives (Ads)
- Follow the **standard ad template** structure.
- Use gradient background.
- One lime accent word max.

### Merchandise / Wearables / Tags
- Conservative palette and high contrast.
- Avoid busy gradients and excessive lime.

---

## Standard Creative Templates

### Ad Creative: Mandatory Elements
Every ad creative must include:

1. **Top-left**: Codebasics SVG logo (blue `#3B82F6`).
2. **Top-right**: YouTube badge: YouTube play icon + **“1 Million+ Subscribers”** + **“4.9 Rating”**.
   - Always exactly **“1 Million+”** (not “1.4M+”, not “1.4 Million+”).
3. **Headline**: Saira Condensed 900, uppercase, with **ONE** lime accent word/phrase.
4. **Visual body**: comparison/timeline/cards/etc.
5. **Bottom bar**: Program name + trust signals + CTA button.

### Bottom Bar Pattern

```
[PROGRAM NAME]     Lifetime Version Access • 100% Refund Policy • Free Portfolio Website     [CTA →]
```

### CTA Button Options
- “Join Program for ₹XX,XXX →”
- “Start Your Journey →”
- “Build Real Projects →”
- “Start for ₹105/Day →”
- “Preview Sample Lessons →”
- “Enroll Now →”

### Lime Accent Rule
Only **one** word/short phrase per creative gets lime `#D7EF3F`.

Examples:
- “STOP LEARNING **DEAD TOOLS.**”
- “REAL PROJECTS VS **TUTORIALS**”
- “WHICH CANDIDATE GETS **THE CALLBACK?**”

---

## YouTube Thumbnail Rules

Thumbnails are **educational** (top of funnel), not bootcamp ads.

### Thumbnail Formula
1. Founder face: **30–40%** of frame, expressive.
2. Bold headline: **3–6 words**, massive (80–120px).
3. Tool/tech logos: alongside/below headline.
4. Gradient background: navy-to-purple.
5. **Do not include**: Codebasics logo, YouTube badge, CTA buttons, prices, trust signals.

### Thumbnail Font Styles
- Saira Condensed 900, strong solid colors.
- Optional outlines/strokes for “provocative” topics.
- Mixed weight (300 + 900) allowed for contrast.

---

## The Cinematic Universe

Use brand characters to dramatize the learner journey.

- **Peter Pandey**: confused beginner; highlight “before” state.
- **Tony Sharma**: shortcut/certificate culture; mock bad habits.
- **Bruce Haryali**: over-thinker; tool fatigue and analysis paralysis.
- **Dhaval/Hemanand**: guides; calm authority.

Rules:
- Mock the mistake, **never the learner**.
- Keep humor secondary to clarity.

---

## The “AtliQ” Standard

Any project visuals, dashboards, datasets, or business context must use **AtliQ** branding.
Never use generic lorem-ipsum business names.

AtliQ universe:
- AtliQ Hardware: consumer electronics
- AtliQ Grands: hospitality
- AtliQ Mart: FMCG retail

---

## Copywriting Guardrails

### Always Do
- Lead with transformation/insight, not price.
- Use real project names (AtliQ Hardware dashboards, supply chain, etc.).
- Include trust signals (refund policy, lifetime access, portfolio site).
- Treat the reader as a smart professional.

### Never Do
- Fake urgency, fear-based marketing.
- Strikethrough pricing.
- Exact salary promises.
- Naming competitors negatively.
- Overpromising speed/ease.

---

## Implementation Notes

### Tokenized Theme (Recommended)
Define these tokens in your design system so artifacts can map consistently:

- `cb.bg`: `#181830`
- `cb.blue`: `#3B82F6`
- `cb.purple`: `#6F53C1`
- `cb.slate`: `#3F4C78`
- `cb.white`: `#FFFFFF`
- `cb.lime`: `#D7EF3F`
- `cb.teal`: `#20C997`
- `cb.orange`: `#FD7E15`
- `cb.pink`: `#D63384`
- `cb.lavender`: `#E1E3FA`

### Accessibility
- Default to white text on navy backgrounds.
- Use lime only for short highlights; it can reduce readability in long runs.
- Maintain sufficient contrast for small Kanit body text.

### When Generating Artifacts
- **Dark-first** by default (navy background + subtle cards).
- Headline: Saira 900 uppercase.
- Body: Kanit 300–400.
- Accents: Blue/Teal; one lime highlight.
- Apply copy guardrails (gimmick-free, no fake urgency, no salary promises).

