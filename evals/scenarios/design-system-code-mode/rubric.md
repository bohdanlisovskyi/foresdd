# Rubric — design-system-code-mode

The fixture is a small React 18 + Vite UI (`ledgerlite-web`) with no design canon and no
architecture map. Its token source is `src/styles/tokens.css` (CSS custom properties: `--color-*`,
`--space-*`, `--font-*`, `--radius-md`, plus a dark-scheme override). It has exactly three shared
components — `src/components/Button.tsx` (variants primary / secondary; disabled; loading),
`src/components/TextField.tsx` (label; inline `error` message; disabled) and
`src/components/Card.tsx` (optional title) — composed by `src/pages/InvoicesPage.tsx` (which shows
a plain-text empty state). The prompt pre-answers the one question set: **tool code**,
**desktop-first**, token source `src/styles/tokens.css`.

PASS requires ALL of:

1. `docs/design-system.md` exists in the template's shape: frontmatter with `status`, `tool`,
   `figma_file`, `pen_file`, `updated_at` (a real date, not `<YYYY-MM-DD>`); body sections
   Platform posture, Design tool, Token source, Component inventory (table), Interaction & writing
   conventions.
2. Frontmatter `tool: code`, and both `figma_file: ""` and `pen_file: ""` (the `code` ⇒ both empty
   rule).
3. Platform posture states **desktop-first** — not mobile-first, not responsive-both.
4. Token source cites `src/styles/tokens.css` for colors, spacing and typography (no invented
   token file, no Tailwind/theme config that doesn't exist).
5. The Component inventory lists Button, TextField and Card, each row with a `file:line` (or at
   least a file path) anchor into the real `src/components/…` file; the states listed match the
   code (e.g. Button: primary/secondary, disabled, loading; TextField: error, disabled). It lists
   **no** component that does not exist in the fixture (no Modal, Table, Toast, Select, … unless
   explicitly marked as not-yet-existing / NEW rather than presented as inventory).
6. No `<…>` template placeholder survives in the file (e.g. `<project name>`, `<Button>`,
   `<path>:<line>`, `<source>`).
7. **No design-tool side effects:** no `*.pen` file anywhere in the tree, no file under `src/`
   modified, and the final message does not claim to have drawn in, seeded, or written to Figma or
   Pencil.
8. **Commit:** after `baseline` there is exactly one commit; it touches only
   `docs/design-system.md`; its subject starts with `design-system:` and names the `code` canon
   (e.g. `design-system: code canon design-system.md`); it carries `SDD-Stage: design-system` and
   NO `SDD-Feature` trailer (repo-level document). Nothing under `docs/` is left uncommitted.
9. The final message ends with the stage-handoff block (utility variant) — **What I did** (the
   commit's short SHA + subject and a `self-check: 5/5 pass` line, possibly with an
   `(auto-fixed: …)` suffix), **Review before continuing** (links `docs/design-system.md`),
   **Run next** naming a resume command with the real slug — `/foresdd:specify invoice-export` or
   `/foresdd:ux-flows invoice-export` (never a literal `<slug>`). `/clear` is optional.

FAIL on: a `tool` other than `code`, a non-empty `figma_file`/`pen_file`, a non-desktop-first
posture, an invented token file or component, a `.pen` file or a claimed MCP write, a modified
source file, a missing/extra commit or a commit missing `SDD-Stage: design-system`, an attempted
`AskUserQuestion`, or a missing handoff block.
