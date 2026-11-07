# Rubric — screens-code-mode

The fixture commits `docs/design-system.md` (`tool: code`, mobile-first, an inventory of Button /
Input / ListItem / EmptyState / Toast — **no sheet or dialog component**) and the `saved-searches`
feature: spec (6 ACs), sad.md (`target_surfaces: [backend-service, web-frontend]`, §6 with
unauthenticated / validation / conflict / empty / not-found branches), ux-flows.md (SCR-01…SCR-03)
and `contracts/openapi.yaml` (400 / 401 / 404 / 409). A correct headless run (`--depth=easy`)
writes the manifest without asking anything and hands off to `tasks`.

PASS requires ALL of:

1. `docs/features/saved-searches/screens.md` exists with the template's sections (Source, Screens,
   New components) and frontmatter `tool: code` with `degraded_from` empty or absent.
2. There is one `### SCR-NN` section for each of SCR-01, SCR-02 and SCR-03 — none missing, none
   invented beyond the inventory (a non-inventory screen is acceptable only if named as a noted gap).
3. Every screen has a `default` state plus at least one `error` or `empty` state, or an explicit
   `N/A: <reason>` row. SCR-02 shows the empty-name (AC-2 / 400) and duplicate-name (AC-4 / 409)
   errors; SCR-03 shows the empty state (AC-5) using `EmptyState`.
4. Every non-default state names its origin — an AC id, a §6 branch, or a contract status/error
   code. No state appears without one.
5. Every component name is either in the design-system inventory or listed in §New components with
   a one-line why-no-primitive-fits justification (the save sheet / delete confirmation have no
   inventory primitive, so they must appear as `NEW:` or be composed from inventory parts with that
   stated). §New components is filled or explicitly «None».
6. Inline ```` ```text ```` wireframes are present for the screens, and no wireframe line is wider
   than 40 characters and no single wireframe block is longer than 16 lines.
7. No `.pen` file was created and no Figma/Pencil tool was used.
8. The run committed `screens.md` (a commit whose subject starts `screens:`), and the final message
   contains the stage-handoff block (What I did / Review before continuing / Run next) forwarding to
   `/foresdd:tasks saved-searches` and reporting the self-check result.

FAIL on: a refusal, an attempted `AskUserQuestion`, a missing SCR section, a happy-path-only
screen, a state with no origin, an unjustified non-inventory component, a wireframe over the size
limit, or a missing handoff block.
