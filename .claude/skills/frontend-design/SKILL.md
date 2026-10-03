---
name: spendly-ui-designer
description: Designs and builds modern, production-ready UI pages and components for Spendly, a Flask + Jinja + vanilla-JS personal expense tracker (github.com/campusx-official/spendly). Use this skill whenever the user asks to design, create, build, redesign, restyle or improve any Spendly page or component, e.g. "design the dashboard page", "create UI for add expense", "build a component for the expense list", "redesign the login page", "improve the profile page", "make a stats card". Trigger even if the user does not say "UI" or "frontend" but is clearly talking about how a Spendly screen looks or feels.
---
 
# Spendly UI Designer
 
Spendly is a lightweight expense tracker built with Flask, SQLite, Jinja2 templates and vanilla JS. Every UI deliverable must fit that stack and look like it belongs to the existing app, so the user can paste the output straight into the repo.
 
## Project constraints (why they matter)
 
The repo's CLAUDE.md forbids frameworks, so React/Tailwind/npm output would be unusable. Follow these:
 
- **Templates**: Jinja2, one `.html` per page, always `{% extends "base.html" %}`.
- **Links**: always `url_for()`, never hardcoded URLs. Static files via `url_for('static', filename='...')`.
- **CSS**: global styles live in `static/css/style.css`. A new page gets its own file, e.g. `static/css/dashboard.css`, linked from the template's head block. No inline `<style>` tags.
- **JS**: vanilla only, in `static/js/main.js` (or a page file). No jQuery, no npm packages.
- **Icons**: Lucide or Heroicons as **inline SVG** (copy the SVG markup, no package install). Use `stroke="currentColor"` so icons inherit text color. Keep one icon family per page.
- **Components**: "modular" means Jinja macros or `{% include %}` partials in `templates/components/` plus class-scoped CSS (BEM-style names such as `.stat-card__value`).
- **Don't touch** routes, DB code or `requirements.txt` unless asked. If a design needs new data, state what the route must pass to the template (variable names and shape) and stop there.
## Step 1: Match the existing design first
 
Consistency beats novelty. Before designing:
 
1. If you have file access, read `static/css/style.css`, `templates/base.html` and one existing page. Reuse its CSS variables, colors, fonts, button and form styles.
2. If you cannot see the code, ask the user for screenshots or the CSS file. Ask once, briefly, then continue with the fallback tokens below only if they decline.
3. Never invent a new color palette or font when one exists.
Fallback tokens (use only when the project defines none; put them in `:root`):
 
```css
:root {
  --space-1: 8px; --space-2: 16px; --space-3: 24px; --space-4: 32px; --space-6: 48px;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px;
  --shadow-sm: 0 1px 2px rgba(16, 24, 40, .06);
  --shadow-md: 0 4px 12px rgba(16, 24, 40, .08);
  --bg: #f6f7fb; --surface: #fff; --border: #e6e8ef;
  --text: #101828; --text-muted: #667085;
  --primary: #4f46e5; --success: #12b76a; --danger: #f04438;
}
```
 
## Step 2: Design rules
 
- Minimal fintech/SaaS look: card-based layout, rounded corners, soft shadows, subtle colors.
- 8px spacing grid. Spacing and type size should create hierarchy (page title, section title, body, muted caption).
- Money values: right-aligned or prominent, tabular numbers (`font-variant-numeric: tabular-nums`), currency symbol consistent with the app, green for income and red for expense only when it adds meaning.
- Every data view needs an **empty state** (icon, one line of guidance, a primary action). Forms need visible labels, inline validation messages and clear focus states.
- Responsive: mobile-first, one breakpoint set (e.g. 640px and 1024px). Tables become stacked cards or scroll inside a wrapper on small screens.
- Accessibility basics: semantic elements, `aria-label` on icon-only buttons, 4.5:1 text contrast, visible `:focus-visible`.
- Avoid: dated UI (heavy borders, default browser buttons, gradients everywhere), clutter, random one-off colors, giant unstructured code dumps.
## Step 3: Output format
 
Always respond in this order:
 
**1. UI Structure (brief)**
- Layout and key sections (3-6 bullets)
- Important UX decisions (2-4 bullets)
- Data the template expects, if any (variable names and shape)
**2. Code**, one labelled block per file, each complete and ready to paste:
- `templates/<page>.html` (or `templates/components/<name>.html`)
- `static/css/<page>.css`
- `static/js/...` only if interaction needs it (keep it minimal)
Give full files, not diffs or fragments. Keep boilerplate minimal; `base.html` already supplies the shell.
 
**3. Notes (2-3 lines max)**: how to wire it up (route name, where to link the CSS) and anything that was assumed.
 
## Example
 
Input: "Design the dashboard page"
Output shape: structure notes (summary cards row, recent expenses list, category breakdown, quick-add button), then `dashboard.html` extending `base.html` using a `stat_card` macro, then `dashboard.css`, then a short note listing the variables the route must pass (`total_spent`, `recent_expenses`, `category_totals`).
 